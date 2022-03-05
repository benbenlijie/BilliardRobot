#if !UNITY_SIMULATION_SDK_DISABLED
using System;
using System.Collections;
using System.IO;
using UnityEngine;

using Unity.Simulation;

using NUnit.Framework;
using UnityEngine.TestTools;

public class ChunkedLoggerTests
{
    [UnityTest]
    public IEnumerator ChunkedLogger_ShouldFlushToFileSystem_AtSpecifiedChunkSize()
    {
        Application.SetStackTraceLogType(LogType.Log, StackTraceLogType.None);
        string basePath = Path.Combine(Configuration.Instance.GetStoragePath(), "Tests");
        string logFilepath = Path.Combine(basePath, "log.txt");

        if (Directory.Exists(basePath))
        {
            Directory.Delete(basePath, true);
        }
        Directory.CreateDirectory(basePath);

        ChunkedUnityLog.CaptureToFile(logFilepath, true, 26);
        Debug.Log("This is a test chunked log file");
        Debug.Log("This is another test chunked log file");
        Debug.Log("Another test chunk of logs");
        yield return new WaitUntil(() => 
        {
            var len = Directory.GetFiles(basePath).Length;
            return len >= 2;
        });
        ChunkedUnityLog.EndCapture();

        var logFiles = Directory.EnumerateFiles(basePath);
        foreach(var f in logFiles)
        {
            var info = new FileInfo(f);
            Debug.Log("file Length: " + info.Length);
            Assert.True(info.Length >= 26);
        }

        Directory.Delete(basePath, true);
    }

    [UnityTest]
    [Timeout(10000)]
    public IEnumerator ChunkedLogger_ShouldFlushToFileSystem_AtSpecifiedChunkTimeout()
    {
        Application.SetStackTraceLogType(LogType.Log, StackTraceLogType.None);
        string basePath = Path.Combine(Configuration.Instance.GetStoragePath(), "Tests");
        string logFilepath = Path.Combine(basePath, "log.txt");

        if (Directory.Exists(basePath))
        {
            Directory.Delete(basePath, true);
        }
        Directory.CreateDirectory(basePath);

        // Save the current logging interval then set it to 0 to prevent it from
        // logging while we're writing out the file for this test.
        float originalLogInterval = TimeLogger.loggingIntervalSeconds;
        TimeLogger.loggingIntervalSeconds = 0;

        ChunkedUnityLog.CaptureToFile(logFilepath, true, 512, 2);
        var testLog = "This is a test log";
        Debug.Log(testLog);
        yield return new WaitUntil(() => Directory.GetFiles(basePath).Length == 1);
        ChunkedUnityLog.EndCapture();

        // Restore the original logging interval.
        TimeLogger.loggingIntervalSeconds = originalLogInterval;

        var fileInfo = new FileInfo(Directory.GetFiles(basePath)[0]);
        int expectedLength = Environment.NewLine.Length + testLog.Length;

        Assert.AreEqual(expectedLength, fileInfo.Length, "Log file length does not match expected test log line");

        Directory.Delete(basePath, true);
    }
}
#endif // !UNITY_SIMULATION_SDK_DISABLED
