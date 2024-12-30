using System;
using System.Collections.Concurrent;

namespace MyApp.Utilities
{
    public class SessionManager
    {
        private static readonly ConcurrentDictionary<string, DateTime> Sessions = new();
        private static readonly TimeSpan SessionTimeout = TimeSpan.FromMinutes(15);

        public static string GetSessionId()
        {
            var sessionId = Guid.NewGuid().ToString();
            Sessions[sessionId] = DateTime.UtcNow;
            return sessionId;
        }

        public static bool IsSessionValid(string sessionId)
        {
            if (Sessions.TryGetValue(sessionId, out var lastAccess))
            {
                if (DateTime.UtcNow - lastAccess < SessionTimeout)
                {
                    Sessions[sessionId] = DateTime.UtcNow; 
                    return true;
                }
                else
                {
                    Sessions.TryRemove(sessionId, out _);
                }
            }
            return false;
        }
    }
}