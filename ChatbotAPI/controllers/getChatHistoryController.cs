using Microsoft.AspNetCore.Mvc;
using Microsoft.Data.SqlClient;
using Dapper;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using System.Collections.Generic;

public class UserQueryResponse
{
    public int QueryId { get; set; }
    public string Question { get; set; }
    public string Response { get; set; }
}

[ApiController]
[Route("api/[controller]")]
public class GetChatHistoryController : ControllerBase
{
    private readonly IConfiguration _configuration;
    private readonly ILogger<GetChatHistoryController> _logger;

    public GetChatHistoryController(IConfiguration configuration, ILogger<GetChatHistoryController> logger)
    {
        _configuration = configuration;
        _logger = logger;
    }

    [HttpGet("session/{sessionId}")]
    public async Task<IActionResult> GetSessionData(Guid sessionId)
    {
        try
        {
            var connectionString = _configuration.GetConnectionString("DefaultConnection") + ";TrustServerCertificate=True";
            using (var connection = new SqlConnection(connectionString))
            {
                await connection.OpenAsync();

                var query = @"
                    SELECT uq.QueryId, uq.Question, cr.Response
                    FROM UserQueries uq
                    LEFT JOIN ChatbotResponses cr ON uq.QueryId = cr.QueryId
                    WHERE uq.SessionId = @SessionId";

                var results = await connection.QueryAsync<UserQueryResponse>(query, new { SessionId = sessionId });

                return Ok(results);
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Internal server error.");
            return StatusCode(500, $"Internal server error: {ex.Message}");
        }
    }
}