# Changelog
## [0.0.10-preview.22] - 2021-01-28
- Updated the toolchain package versions required for cross-compilation of CloudRendering from Mac/Windows to Linux IL2CPP.
- Added support for cloudrendering to set resolution from player settings or provide player resolution setting config via scriptable object.

## [0.0.10-preview.21] - 2020-12-07

Additions:

- Added a NameGenerator class, with associated NameComponents and Editor.
  This class, given a base path will generate names based on the components you add in the editor.
  Components include: Path (dir, name, ext), Label, Sequence (auto increment), Timestamp (various formats), and FrameNumber. To create a NameGenerator asset, use the right click Create menu, and choose NameGenerator from the Simulation sub menu.
- Added a TimeScale class. This class allows you to specify the time scale that you would like to run the simulation at. Additionally, it also supports an auto option, which will calculate the average frame delta time, and drive the time scale by the appropriate value to try to utilize 100% of the main thread. There is also an option to specify the approximate utilization.
- The CameraGrab and DepthGrab components now support a NameGenerator which can be used to override the current naming scheme.
- Several warnings have been added as a pre-build step to validate compatibility with Unity Simulation at build time. The checks include: Ensure build target is Linux64, and that the graphics API is supported for the build target.
- AsyncRequest has been modified to include an instanced property that allows you to specify the maximum lifetime of the request in frames. Once the request reaches this age in number of frames, it is automatically completed synchronously.
- The default log level for the logger has been reduced to Info from Verbose.
  This will reduce the noise in the editor and player logs. You can set this to whatever value you like from scripts.
- A timestamp has been added to log output. This is useful for searching the log to find output at a specific time. It can also be used to determine the length of the simulation.
- Added several shutdown conditions (similar to FrameLimit/TimeLimit) that can be invoked via scripting. The Manager class now has a ShutdownCondition property it checks, and if that property returns true, then shutdown is initiated. You can implement your own shutdown conditions by defining a class that implements ICondition, and setting the ShutdownCondition property to use an instance of your class. In addition, several helper methods have been added to the Manager class,
  they are: ShutdownAfterFrames, ShutdownAfterSimSeconds, and ShutdownAfterWallSeconds.
- Added a Timer class which abstracts various ways of measuring time, from Time.deltaTime to Stopwatch. This is now used in a few places, such as the TimeLimit component, where you can specify how to measure time.
- Added a build define UNITY_SIMULATION_SDK_DISABLED around the core package code. This can be set to disable the compilation of the core package. This can be used to compile out the core package in certain builds.

Deprecations:

- Options.maxRequestStartFramesToWait has been marked obsolete and will be removed.

Bug Fixes:

- Fixed a bug in FrameLimit component, where it wasn't properly incrementing the frame counter.
- The signed URL uploader once again specifies the correct content-type for uploading.
- The time for fetching the signed upload URL is now timed, and logged when verbose logging is enabled.

## [0.0.10-preview.20] - 2020-10-27
- Adding a prebuild step to import crosscompiling toolchain for cloudrendering build target.
- Added an ability to set localPersistentDataPath for captured data via Simulation Configuration instance.

## [0.0.10-preview.19] - 2020-08-26

- Make the Options class public (was internal)

## [0.0.10-preview.18] - 2020-08-19

- Fix for Compile issues with Unity 2018.4.
- Fix for JobSystem execution context issue for Unity 2018.4.
- Fix for an issue where Configuration manager was not accepting spaces in the appParam file path.
- Add More test coverage.

## [0.0.10-preview.17] - 2020-08-4

- Fix issue with previous version caused by an incorrect merge.

## [0.0.10-preview.16] - 2020-08-3

- AsyncRequests are now tracked by default, and the Manager will wait on shutdown for them to complete.
  This fixes an issue where requests that were in flight would be ignored because the shutdown was in process.
- Added an option AsyncRequest.maxAsyncRequestFrameAge which when set, completes requests in flight when they reach this age.
  This is useful for requests that have native containers using Allocator.Temp which auto frees at 4 frames.
- QueueEndOfFrameItem has been deprecated. Please use Manager.Instance.QueueForEndOfFrame instead.
- Uploading of the Player.Log has been removed. This functionality is now handled by the Unity Simulation Agent in the cloud.

## [0.0.10-preview.15] - 2020-07-21

- Adding an option to ignore maxElapsedTime for the logger to flush down to the file system based upon the file size only.
- Fix for GetParams() API where appParams for a struct was not getting set.
- Fix for an issue where logger was producing an additional empty file at the end of the simulation.
- Fix for hardware spec logs getting spammed while running in the editor.
- Fix for AsyncRequest  factory for IL2CPP.
- Added MaxParallelism to MaxWorkerCount in Cloud and 3 in editor.
- Added unhandled exception handler to catch exceptions from other threads.
- ShutdownNotification is now sent from LateUpdate.

## [0.0.10-preview.14] - 2020-06-16

- Fix for regression issue caused by updating the core tests asmdef file making it incompatible with unity version 2019.1 and below.
- Fix for c# job scheduling off of main thread (ESIM-1338, ESIM-1337).

## [0.0.10-preview.13] - 2020-05-14

- Fix for regression, uploading the player log to logs location.
- Remove Debug.Log statement causing unintended output.

## [0.0.10-preview.12] - 2020-05-04

C# Job system support
Retry attempt for failed uploads in Signlynx.
End to end tests on USim
TimeLogger: FPS calculated correctly.
TimeLogger: Elapsed times aligned correctly from start.
Added TimeLimit component (exits when time limit is up)
Added FrameLimit component (exits application after a number of frames)
Added Hardware Specs for Mac and Linux.
Added ContinuousEvents (piecewise aggregated signal for given metric)
Bug: ChunkedStream flushes on shutdown.
Removed FakeDataConsumer to reduce noise.

## [0.0.10-preview.11] - 2020-04-28

Update .npmignore to include upm-ci.log

## [0.0.10-preview.10] - 2020-04-27

Treat full Player.Log and profiler log as artifact

## [0.0.10-preview.9] - 2020-04-10

Support new storage structure that splits data and logs

## [0.0.10-preview.8] - 2020-03-16

Fix warnings in package.

## [0.0.10-preview.7] - 2020-03-16

Add QAReport.md and README.md to .npmignore

## [0.0.10-preview.6] - 2020-03-06

Fixed Obsolete messages to work for validation.

## [0.0.10-preview.5] - 2020-03-06

Fix date format.
Fix changelog format.

## [0.0.10-preview.4] - 2020-03-06

Reverted rename of LICENSE.md file which caused package validation to fail.

## [0.0.10-preview.3] - 2020-03-05

Renamed LICENSE.md to LICENSE_S.md
Updated license with final text.

## [0.0.10-preview.2] - 2020-03-05

Updated for testing continuous integration.

## [0.0.10-preview.1] - 2020-02-11

This package contains core funtionality required by unity simulations.
First package release based on unity package version 1.0.11.
