using System;
using System.IO;
using System.Text;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading;
using System.Threading.Tasks;

#if UNITY_EDITOR
using UnityEngine;
using UnityEditor;
#endif

namespace Unity.Simulation.Client
{
    internal static class Transaction
    {
        public static HttpClient client { get; private set; }

        static Transaction()
        {
            client = new HttpClient();
            client.Timeout = TimeSpan.FromSeconds(Config.timeoutSecs);
            client.DefaultRequestHeaders.TransferEncodingChunked = true;
        }

        internal static string accessToken { get; set; }

        internal static void SetAuthHeaders(HttpRequestHeaders headers, string accessToken)
        {
#if UNITY_EDITOR
            if (string.IsNullOrEmpty(accessToken))
                accessToken = Project.accessToken;
#endif
            Debug.Assert(!string.IsNullOrEmpty(accessToken), "SetAuthHeaders: access token cannot be null or empty");
            headers.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json" ));
            headers.UserAgent.Add(new ProductInfoHeaderValue("usim-cli", "0.0.0"));
            headers.Authorization = new AuthenticationHeaderValue("Bearer", accessToken);
        }

        internal static async Task Request(HttpMethod method, string url, string accessToken, HttpContent content, string contentType = null, CancellationTokenSource cancellationTokenSource = null)
        {
            using (var message = new HttpRequestMessage(method, url))
            {
                SetAuthHeaders(message.Headers, accessToken);

                if (contentType == null)
                    contentType = "application/json";

                if (content != null)
                    message.Content = content;

                var ct = cancellationTokenSource == null ? new CancellationTokenSource(1000 * Config.timeoutSecs).Token : cancellationTokenSource.Token;
                var response = await client.SendAsync(message, HttpCompletionOption.ResponseContentRead, ct).ConfigureAwait(false);
                if (!response.IsSuccessStatusCode)
                    throw new Exception($"Request to {url} failed for reason '{response.ReasonPhrase}'");
            }
        }

        internal static async Task<string> UploadAsync(string url, string name, string location, string accessToken, string contentType = null, CancellationTokenSource cancellationTokenSource = null, Action<float> progress = null)
        {
            var details = GetUploadURL(url, name, accessToken);

            using (var stream = new FileStream(location, FileMode.Open))
            using (var streamContent = new StreamContentWithProgress(stream, cancellationTokenSource, progress))
            {
                await Request(HttpMethod.Put, details.Item1, accessToken, streamContent, contentType, cancellationTokenSource).ConfigureAwait(false);
                return details.Item2;
            }
        }

        internal static string Upload(string url, string name, string inFile, bool useTransferUrls, string accessToken)
        {
            return Upload(url, name, File.ReadAllBytes(inFile), useTransferUrls, accessToken);
        }

        internal static string Upload(string url, string name, byte[] data, bool useTransferUrls, string accessToken)
        {
            string entityId = null;

            Action<HttpRequestMessage> action = message =>
            {
                Transaction.SetAuthHeaders(message.Headers, accessToken);
                message.Content = new ByteArrayContent(data);
                var request = Transaction.client.SendAsync(message);
                request.Wait(TimeSpan.FromSeconds(Config.timeoutSecs));

                if (!request.Result.IsSuccessStatusCode)
                {
                    throw new Exception("Upload failed " + request.Result.ReasonPhrase);
                }

                var payload = request.Result.Content.ReadAsStringAsync();
                payload.Wait();

                if (!string.IsNullOrEmpty(payload.Result))
                {
                    Debug.Assert(false, "Need to pull id from response");
                    // set entity return id here
                }
            };

            if (useTransferUrls)
            {
                var tuple = GetUploadURL(url, name, accessToken);
                entityId  = tuple.Item2;
                using (var message = new HttpRequestMessage(HttpMethod.Put, tuple.Item1))
                {
                    action(message);
                }
            }
            else
            {
                using (var message = new HttpRequestMessage(HttpMethod.Post, url))
                {
                    action(message);
                }
            }

            Debug.Assert(!string.IsNullOrEmpty(entityId));

            return entityId;
        }

        internal static string PostJSON(string url, byte[] data, string accessToken)
        {
            using (var message = new HttpRequestMessage(HttpMethod.Post, url))
            {
                Transaction.SetAuthHeaders(message.Headers, accessToken);
                message.Content = new ByteArrayContent(data);
                message.Content.Headers.Add("Content-Type", "application/json");
                var request = Transaction.client.SendAsync(message);
                request.Wait(TimeSpan.FromSeconds(Config.timeoutSecs));

                if (!request.Result.IsSuccessStatusCode)
                {
                    throw new Exception("Upload failed " + request.Result.ReasonPhrase);
                }

                var payload = request.Result.Content.ReadAsStringAsync();
                payload.Wait();
                return payload.Result;
            }
        }

        internal static string GetJSON(string url, string accessToken)
        {
            using (var message = new HttpRequestMessage(HttpMethod.Get, url))
            {
                Transaction.SetAuthHeaders(message.Headers, accessToken);
                var request = Transaction.client.SendAsync(message);
                request.Wait(TimeSpan.FromSeconds(Config.timeoutSecs));

                if (!request.Result.IsSuccessStatusCode)
                {
                    throw new Exception("GetJSON failed " + request.Result.ReasonPhrase);
                }

                var payload = request.Result.Content.ReadAsStringAsync();
                payload.Wait();

                return payload.Result;
            }
        }

        internal static void Download(string url, string id, string outFile, bool useTransferUrls, string accessToken)
        {
            if (!Directory.Exists(outFile))
                throw new Exception("Download location must exist " + outFile);

            var data = Transaction.Download(url, id, useTransferUrls, accessToken);
            if (data != null)
                File.WriteAllBytes(outFile, data);
        }

        internal static string GetDownloadUrl(string url, string id, bool useTransferUrls, string accessToken)
        {
            return useTransferUrls ? GetDownloadDetails(url, id, accessToken).Item1 : $"{url}/{id}";
        }

        internal static byte[] Download(string url, string id, bool useTransferUrls, string accessToken)
        {
            url = useTransferUrls ? GetDownloadDetails(url, id, accessToken).Item1 : $"{url}/{id}";
            using (var message = new HttpRequestMessage(HttpMethod.Get, url))
            {
                Transaction.SetAuthHeaders(message.Headers, accessToken);
                var request = Transaction.client.SendAsync(message);
                request.Wait(TimeSpan.FromSeconds(Config.timeoutSecs));

                if (!request.Result.IsSuccessStatusCode)
                {
                    throw new Exception("Download failed " + request.Result.ReasonPhrase);
                }

                var payload = request.Result.Content.ReadAsStringAsync();
                payload.Wait();

                return Encoding.UTF8.GetBytes(payload.Result);
            }
        }

        // first = upload_uri, second = entity_id
        internal static Tuple<string, string> GetUploadURL(string url, string path, string accessToken)
        {
            using (var message = new HttpRequestMessage(HttpMethod.Post, url))
            {
                Transaction.SetAuthHeaders(message.Headers, accessToken);
                message.Content = new StringContent(JsonUtility.ToJson(new UploadInfo(Path.GetFileName(path), "Placeholder description")), Encoding.UTF8, "application/json");
                var request = Transaction.client.SendAsync(message);
                request.Wait(TimeSpan.FromSeconds(Config.timeoutSecs));

                if (!request.Result.IsSuccessStatusCode)
                {
                    throw new Exception($"GetUploadURL failed {request.Result.ReasonPhrase}");
                }

                var payload = request.Result.Content.ReadAsStringAsync();
                payload.Wait();

                var data = JsonUtility.FromJson<UploadUrlData>(payload.Result);
                return new Tuple<string, string>(data.upload_uri, data.id);
            }
        }

        // first = download_url, second = entity name
        internal static Tuple<string, string> GetDownloadDetails(string url, string id, string accessToken)
        {
            using (var message = new HttpRequestMessage(HttpMethod.Get, $"{url}/{id}"))
            {
                Transaction.SetAuthHeaders(message.Headers, accessToken);
                var request = Transaction.client.SendAsync(message);
                request.Wait(TimeSpan.FromSeconds(Config.timeoutSecs));

                if (!request.Result.IsSuccessStatusCode)
                {
                    throw new Exception("GetDownloadDetails failed " + request.Result.ReasonPhrase);
                }

                var payload = request.Result.Content.ReadAsStringAsync();
                payload.Wait();

                var data = JsonUtility.FromJson<DownloadDetails>(payload.Result);
                return new Tuple<string, string>(data.download_uri, data.name);
            }
        }

        internal static void Delete(string url, string id, string entityType, string accessToken)
        {
            using (var message = new HttpRequestMessage(HttpMethod.Delete, $"{url}/{id}"))
            {
                Transaction.SetAuthHeaders(message.Headers, accessToken);
                var request = Transaction.client.SendAsync(message);
                request.Wait(TimeSpan.FromSeconds(Config.timeoutSecs));

                if (!request.Result.IsSuccessStatusCode)
                {
                    throw new Exception($"Delete {id} failed {request.Result.ReasonPhrase}");
                }

                var payload = request.Result.Content.ReadAsStringAsync();
                payload.Wait();
            }
        }
    }
}
