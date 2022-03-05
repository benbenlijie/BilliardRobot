#if UNITY_EDITOR
using System;
using System.IO;
using System.Net;
using System.Net.Http;
using System.Threading;
using System.Threading.Tasks;
using System.Collections.Concurrent;

using UnityEditor;

namespace Unity.Simulation.Client
{
    public class StreamContentWithProgress : StreamContent
    {
        public int chunkSize { get; set; } = 4096;

        public Action<float> progress { get; set; }

        public StreamContentWithProgress(Stream stream, CancellationTokenSource cancellationTokenSource = null, Action<float> progress = null)
            : base(stream)
        {
            _content = stream;
            _totalBytes = (int)_content.Length;
            this.progress = progress;
            _cancellationTokenSource = cancellationTokenSource;

            EditorApplication.update += UpdateProgressOnMainThread;
        }

        // Non-Public Methods

        Stream _content;
        int    _totalBytes;
        int    _bytesWritten;
        CancellationTokenSource _cancellationTokenSource;

        void UpdateProgressOnMainThread()
        {
            progress?.Invoke((float)_bytesWritten / (float)_totalBytes);

            if (_bytesWritten == _totalBytes || (_cancellationTokenSource != null && _cancellationTokenSource.Token.IsCancellationRequested))
                EditorApplication.update -= UpdateProgressOnMainThread;
        }

        protected override async Task SerializeToStreamAsync(Stream stream, TransportContext context)
        {
            _totalBytes = (int)_content.Length;
            _bytesWritten = 0;
            
            var buffer = new byte[chunkSize];
            while (_bytesWritten < _totalBytes)
            {
                int size = Math.Min(chunkSize, _totalBytes - _bytesWritten);
                await _content.ReadAsync(buffer, 0, size);
                await stream.WriteAsync(buffer, 0, size);
                _bytesWritten += size;
            }
        }
    }
}
#endif // UNITY_EDITOR
