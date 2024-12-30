using Microsoft.AspNetCore.Mvc;
using Microsoft.Data.SqlClient;
using Dapper;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;

public class QueryRequest
{
    public string Query { get; set; } = string.Empty;
}

public class QueryResponse
{
    public string answer { get; set; } = string.Empty;
}

[ApiController]
[Route("api/[controller]")]
public class ChatbotController : ControllerBase
{
    private readonly IConfiguration _configuration;
    private readonly HttpClient _httpClient;
    private readonly ILogger<ChatbotController> _logger;

    public ChatbotController(IConfiguration configuration, HttpClient httpClient, ILogger<ChatbotController> logger)
    {
        _configuration = configuration;
        _httpClient = httpClient;
        _logger = logger;
    }

    [HttpPost("ask")]
    public async Task<IActionResult> AskQuestion([FromBody] QueryRequest queryRequest)
    {
        try
        {
            
            var connectionString = _configuration.GetConnectionString("DefaultConnection") + ";TrustServerCertificate=True";

            Guid sessionId;

            using (var connection = new SqlConnection(connectionString))
            {
                await connection.OpenAsync();

  
                sessionId = await connection.QueryFirstOrDefaultAsync<Guid>(
                    @"SELECT TOP 1 SessionId 
                      FROM UserQueries 
                      WHERE SessionExpiration >= GETDATE() 
                      ORDER BY QueryId DESC");

                if (sessionId == Guid.Empty)
                {

                    sessionId = Guid.NewGuid();
                }
            }


            var response = await _httpClient.PostAsync("http://localhost:8000/ask",
                new StringContent(JsonSerializer.Serialize(queryRequest), Encoding.UTF8, "application/json"));

            if (!response.IsSuccessStatusCode)
            {
                return StatusCode((int)response.StatusCode, await response.Content.ReadAsStringAsync());
            }

            var responseContent = await response.Content.ReadAsStringAsync();
            _logger.LogInformation("Response from FastAPI: {ResponseContent}", responseContent);

            var queryResponse = JsonSerializer.Deserialize<QueryResponse>(responseContent);

            if (queryResponse == null)
            {
                return StatusCode(500, "Failed to deserialize response from FastAPI server.");
            }


            using (var connection = new SqlConnection(connectionString))
            {
                await connection.OpenAsync();

                var queryId = await connection.ExecuteScalarAsync<int>(
                    @"INSERT INTO UserQueries (SessionId, Question, SessionExpiration) 
                      VALUES (@SessionId, @Question, DATEADD(MINUTE, 15, GETDATE()));
                      SELECT SCOPE_IDENTITY();",
                    new { SessionId = sessionId, Question = queryRequest.Query });

                await connection.ExecuteAsync(
                    @"INSERT INTO ChatbotResponses (QueryId, Response) 
                      VALUES (@QueryId, @Response);",
                    new { QueryId = queryId, Response = queryResponse.answer });
            }

            return Ok(queryResponse);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error occurred while processing the request.");
            return StatusCode(500, $"Internal server error: {ex.Message}");
        }
    }
}

