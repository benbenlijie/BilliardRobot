# Changelog

## [0.0.10-preview.10] - 2020-11-03

- Added a generic Run On Unity Simulation window. You can show this window by invoking `GetWindow<CreateBuildEditorWindow>().Show();`
- Added support for batch uploading of AppParams to USim. Supports uploading a dictionary of objects, and either an array of objects or an array of preserialized JSON.
- Added support for retrieving an array of all RunDefinitions.
- Project.BuildProject now takes optional BuildOptions, and also returns true or false depending on the build success status.
- Fixed a bug downloading the Player.Log where the name was incorrect.
- Fixed a bug with the upload build progress that would cause the progress bar to not advance properly.

## [0.0.10-preview.9] - 2020-05-15

- Fix a bug in ZipUtility that caused builds to not zip correctly on windows.

## [0.0.10-preview.8] - 2020-05-13

- Added a bug fix for an issue where projectIdState was not getting set after re-binding the project.
- Added an API for getting accessToken by passing user credentials in batchmode.
- Added an overload for SetAppParam API that takes in a json string
- Added a fix for an issue where background monitoring of simulation run execution will get aborted on domain reload.
- Added a fix for an issue where background run execution monitoring thread was throwing an abort exception on domain reload.

## [0.0.10-preview.7] - 2020-05-04

- Async Build upload support
- Events for ProjectID changed and AccessToken changed.
- Bug fixes: ESIM-941 and AISV-399
- Added more tests.
- Added UploadBuildAsync with progress support.
- Added callbacks for projectId, accessToken and client readiness state changes.
- Added callback for when a run completes.
- Added TestBuild base class for adding examples easily.
- Increased default API timeout to 7200 seconds for uploading large builds.
- Support for 2018.4 restored.

## [0.0.10-preview.6] - 2020-04-28

- Update .npmignore to include upm-ci.log

## [0.0.10-preview.5] - 2020-04-21

- All API calls will now throw an InvalidOperationException if no valid Unity project id exists.
- Fixes ESIM-941 and AISV-399
- Add PropertyIdState enum.
- Add handler to respond to UnityConnect StateChanged delegate.
- Add events for accessTokenChanged and projectIdChanged.

## [0.0.10-preview.4] - 2020-04-16

- Set the default timeout for the HttpClient instance to Config.timeoutSecs.
- Expose Config.timeoutSecs setter.
- Config.timeoutSecs defaults to 7200.

## [0.0.10-preview.3] - 2020-03-16

Added .npmignore to remove QAReport.md and README.md from package.

## [0.0.10-preview.2] - 2020-03-09

- Fix license file.
- Validation suite fixes.

## [0.0.10-preview.1] - 2020-02-11

This package contains functionality to use the simulation service using scripts.
First package release based on unity package version 1.0.11.

