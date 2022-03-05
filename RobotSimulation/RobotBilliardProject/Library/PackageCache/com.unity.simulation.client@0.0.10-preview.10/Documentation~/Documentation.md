# USim C# Client Documentation.

USim C# client implements the USim REST API as a C# package that can be used to upload, configure, and execute builds on the Unity Simulation service.

## Examples

```csharp
[MenuItem("Simulation/Cloud/Build")]
public static void BuildProject()
{
    var scenes = new string[]
    {
        "Assets/Legacy/cluster.unity",
        "Assets/Legacy/test_scene.unity"
    };
    Project.BuildProject("./test_linux_build", "TestBuild", scenes);
}
```

```csharp
var run = Run.Create("test", "test run");
var sysParam = API.GetSysParams()[0];
run.SetSysParam(sysParam);
run.SetBuildLocation(zipPath);
run.SetAppParam("test", new TestAppParam(1), 1);
run.Execute();

while (!run.completed)
    ;

Debug.Log("Run completed.");
```

```csharp
[MenuItem("Simulation/Login")]
public static void Login()
{
    API.Login();
}

[MenuItem("Simulation/Build And Upload")]
public static void BuildAndUploadProject()
{
    var window = GetWindow<ClientDialog>(utility: true, title: "Build And Upload", focus: true);
    if (window != null)
    {
        window.minSize = new Vector2(kWindowWidth, kWindowHeight);
        window.maxSize = window.minSize;
        window.options = Option.Build | Option.Zip | Option.Upload | Option.HelpText | Option.Buttons;
        window.ShowUtility();
    }
}
```

## Parity With CLI

| CLI | C# |
| ----------- | ----------- |
| usim login auth | Auth.Login |
| usim refresh auth | Auth.Refresh |
| usim get projects | Project.GetProjects |
| usim describe project | N/A |
| usim activate project | Project.Activate |
| usim deactivate project | Project.Deactivate |
| usim get sys-params | API.GetSysParams |
| usim get app-params | N/A |
| usim upload app-param | API.UploadAppParam\<T\> |
| usim download app-param | API.DownloadAppParam\<T\> |
| usim get builds | N/A |
| usim zip build | Project.CompressBuild |
| usim upload build | API.UploadBuild |
| usim download build | API.DownloadBuild |
| usim get runs | N/A |
| usim describe run | N/A |
| usim define run | Run.Create |
| usim upload run | API.UploadRunDefinition |
| usim execute run | run.Execute |
| usim cancel run-execution | N/A |
| usim describe run-execution | Run.Describe |
| usim download manifest | Run.GetManifest |
| usim summarize run-execution | Run.Summarize |
| usim logs | N/A |
