#if !UNITY_SIMULATION_SDK_DISABLED
using System;
using System.Collections;
using System.IO;
using UnityEngine;

using Unity.Simulation;

using NUnit.Framework;
using NUnit.Framework.Internal;
using UnityEngine.TestTools;

public class ConfigurationTests
{
    [Test]
    public void BucketName_And_StoragePath_Returns_AsExpected()
    {
        var expectedBucketName = "test-bucket";
        var expectedStoragePath = "folder1/folder2";

        Configuration.Instance.SimulationConfig = new Configuration.SimulationConfiguration()
        {
            storage_uri_prefix = "gs://test-bucket/folder1/folder2"
        };

        Debug.Log("Storage Prefix: " + Configuration.Instance.SimulationConfig.storage_uri_prefix);

        string actualBucketName = Configuration.Instance.SimulationConfig.bucketName;
        string actualStoragePath = Configuration.Instance.SimulationConfig.storagePath;

        Debug.Assert(actualBucketName == expectedBucketName, $"Bucket name returned: {actualBucketName} is not as expected");
        Debug.Assert(actualStoragePath == expectedStoragePath, $"Storage Path returned: {actualStoragePath} is not as expected");
    }

    [Serializable]
    public struct Test
    {
        public string msg;
    }
    [UnityTest]
    public IEnumerator AppParamPath_With_Spaces()
    {
        var folderWithSpace = "Folder With Space";
        var path = Path.Combine(Application.persistentDataPath, folderWithSpace);
        if (!Directory.Exists(path))
            Directory.CreateDirectory(path);
        File.WriteAllText(path + "/test.json", "{ \"msg\" : \"test\"}");
        Configuration.Instance.SimulationConfig = new Configuration.SimulationConfiguration()
        {
            app_param_uri = "file://" + path + "/test.json"
        };

        var config = Configuration.Instance.GetAppParams<Test>();
        Assert.IsTrue(config.msg.Equals("test"));

        yield return null;
    }
}
#endif // !UNITY_SIMULATION_SDK_DISABLED
