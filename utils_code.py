import json
from typing import Literal
import re

available_languages = [
    "Python-Requests",
    "Python-Aiohttp",
    "C",
    "C#",
    "Clojure",
    "Go",
    "HTTP",
    "Java",
    "JavaScript-Fetch",
    "JavaScript-XMLHttpRequest",
    "Kotlin",
    "Node.js-Requests",
    "Node.js-Axios",
    "Node.js-Unirest",
    "PHP",
    "R",
    "Ruby",
    "Shell",
    "Rust",
]


def generate_code_snippet(
    language: Literal[
        "Python-Requests",
        "Python-Aiohttp",
        "C",
        "C#",
        "Clojure",
        "Go",
        "HTTP",
        "Java",
        "JavaScript-Fetch",
        "JavaScript-XMLHttpRequest",
        "Kotlin",
        "Node.js-Requests",
        "Node.js-Axios",
        "Node.js-Unirest",
        "PHP",
        "R",
        "Ruby",
        "Shell",
        "Rust",
    ] = "Python-Requests",
    long_url: str = "https://example.com",
    alias: str = None,
    password: str = None,
    max_clicks: int = None,
):

    if language == "Python-Requests":
        payload = {
            "url": long_url,
        }

        if alias is not None:
            payload["alias"] = alias
        if password is not None:
            payload["password"] = password
        if max_clicks is not None:
            payload["max-clicks"] = str(max_clicks)

        payload_str = json.dumps(payload, indent=4)

        return (
            f"""import requests

url = "https://spoo.me/"

payload = {payload_str}
headers = {{
    "Accept": "application/json",
}}

response = requests.post(url, data=payload, headers=headers)

if response.status_code == 200:
    print(response.json())
else:
    print(response.text)""",
            "python",
        )

    elif language == "Python-Aiohttp":
        payload = {
            "url": long_url,
        }

        if alias is not None:
            payload["alias"] = alias
        if password is not None:
            payload["password"] = password
        if max_clicks is not None:
            payload["max-clicks"] = str(max_clicks)

        payload_str = json.dumps(payload, indent=4)

        return (
            f"""import aiohttp
import asyncio

url = "https://spoo.me/"

payload = {payload_str}
headers = {{
    "Accept": "application/json",
}}

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=headers) as response:
            if response.status == 200:
                print(await response.json())
            else:
                print(await response.text())

asyncio.run(main())""",
            "python",
        )

    elif language == "C":
        payload = f"url={long_url}"

        if alias is not None:
            payload += f"&alias={alias}"
        if password is not None:
            payload += f"&password={password}"
        if max_clicks is not None:
            payload += f"&max-clicks={max_clicks}"

        return (
            f"""CURL *hnd = curl_easy_init();

curl_easy_setopt(hnd, CURLOPT_CUSTOMREQUEST, "POST");
curl_easy_setopt(hnd, CURLOPT_URL, "https://spoo.me/");

struct curl_slist *headers = NULL;
headers = curl_slist_append(headers, "Accept: application/json");
curl_easy_setopt(hnd, CURLOPT_HTTPHEADER, headers);

char *output = curl_easy_escape(hnd, "{payload}", 0);
curl_easy_setopt(hnd, CURLOPT_POSTFIELDS, output);
curl_free(output);

CURLcode ret = curl_easy_perform(hnd);""",
            "c",
        )

    elif language == "Clojure":
        form_params = f':url "{long_url}"'

        if alias is not None:
            form_params += f' :alias "{alias}"'
        if password is not None:
            form_params += f' :password "{password}"'
        if max_clicks is not None:
            form_params += f' :max-clicks "{max_clicks}"'

        return (
            f"""
(require '[clj-http.client :as client])

(client/post "https://spoo.me/" {{:form-params {{{form_params}}}
                                :accept :json}})
""",
            "clojure",
        )

    elif language == "C#":
        form_params = f'{{ "url", "{long_url}" }}'

        if alias is not None:
            form_params += f', {{ "alias", "{alias}" }}'
        if password is not None:
            form_params += f', {{ "password", "{password}" }}'
        if max_clicks is not None:
            form_params += f', {{ "max-clicks", "{max_clicks}" }}'

        return (
            f"""using System.Net.Http;
using System.Net.Http.Headers;
using System.Collections.Generic;

var client = new HttpClient();
var request = new HttpRequestMessage
{{
    Method = HttpMethod.Post,
    RequestUri = new Uri("https://spoo.me/"),
    Headers =
    {{
        {{ "Accept", "application/json" }},
    }},
    Content = new FormUrlEncodedContent(new Dictionary<string, string>
    {{
        {form_params}
    }}),
}};
try
{{
    using (var response = await client.SendAsync(request))
    {{
        response.EnsureSuccessStatusCode();
        var body = await response.Content.ReadAsStringAsync();
        Console.WriteLine(body);
    }}
}}
catch (HttpRequestException ex)
{{
    Console.WriteLine($"HTTP request error: {{ex.Message}}");
}}""",
            "csharp",
        )

    elif language == "Go":
        form_params = f"url={long_url}"

        if alias is not None:
            form_params += f"&alias={alias}"
        if password is not None:
            form_params += f"&password={password}"
        if max_clicks is not None:
            form_params += f"&max-clicks={max_clicks}"

        return (
            f"""package main

import (
    "context"
    "fmt"
    "io"
    "net"
    "net/http"
    "strings"
    "time"
)

func main() {{
    // Set DNS resolver to use Google's public DNS server
    net.DefaultResolver = &net.Resolver{{
        Dial: func(ctx context.Context, network, address string) (net.Conn, error) {{
            d := net.Dialer{{Timeout: 500 * time.Millisecond}}
            return d.DialContext(ctx, "udp", "8.8.8.8:53")
        }},
    }}

    url := "https://spoo.me/"
    payload := strings.NewReader("{form_params}")

    req, err := http.NewRequest("POST", url, payload)
    if err != nil {{
        fmt.Println("Error creating request:", err)
        return
    }}

    req.Header.Add("Content-Type", "application/x-www-form-urlencoded")
    req.Header.Add("Accept", "application/json")

    res, err := http.DefaultClient.Do(req)
    if err != nil {{
        fmt.Println("Error making request:", err)
        return
    }}

    defer res.Body.Close()
    body, err := io.ReadAll(res.Body)
    if err != nil {{
        fmt.Println("Error reading response:", err)
        return
    }}

    fmt.Println(res)
    fmt.Println(string(body))
}}""",
            "go",
        )

    elif language == "HTTP":
        form_params = f"url={long_url}"

        if alias is not None:
            form_params += f"&alias={alias}"
        if password is not None:
            form_params += f"&password={password}"
        if max_clicks is not None:
            form_params += f"&max-clicks={max_clicks}"

        return (
            f"""
POST / HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Accept: application/json
Host: spoo.me
Content-Length: {len(form_params)}

{form_params}""",
            "",
        )

    elif language == "Java":
        form_params = f"url={long_url}"

        if alias is not None:
            form_params += f"&alias={alias}"
        if password is not None:
            form_params += f"&password={password}"
        if max_clicks is not None:
            form_params += f"&max-clicks={max_clicks}"

        return (
            f"""import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class HttpRequestExample {{

    public static void main(String[] args) {{
        // Define the URL
        String url = "https://spoo.me/";

        // Build the request body
        String requestBody = "{form_params}";

        // Create and configure the HttpClient
        HttpClient httpClient = HttpClient.newHttpClient();

        // Build the HttpRequest
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("Content-Type", "application/x-www-form-urlencoded")
                .header("Accept", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(requestBody))
                .build();

        try {{
            // Send the request and receive the response
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());

            // Print the response status code and body
            System.out.println("Response Code: " + response.statusCode());
            System.out.println("Response Body: " + response.body());
        }} catch (Exception e) {{
            e.printStackTrace();
        }}
    }}
}}""",
            "java",
        )

    elif language == "JavaScript-Fetch":
        form_params = f"url: '{long_url}'"

        if alias is not None:
            form_params += f",\n\t\talias: '{alias}'"
        if password is not None:
            form_params += f",\n\t\tpassword: '{password}'"
        if max_clicks is not None:
            form_params += f",\n\t\t'max-clicks': '{max_clicks}'"

        return (
            f"""const url = 'https://spoo.me/';
const options = {{
    method: 'POST',
    headers: {{
        'content-type': 'application/x-www-form-urlencoded',
        Accept: 'application/json',
    }},
    body: new URLSearchParams({{
        {form_params}
    }})
}};

async function shortUrl() {{
    try {{
        const response = await fetch(url, options);

        if (!response.ok) {{
            throw new Error(`HTTP error! Status: ${{response.status}}`);
        }}

        const result = await response.text();

        console.log(result);
    }} catch (error) {{
        console.error(error);
    }}
}}
shortUrl();""",
            "js",
        )

    elif language == "JavaScript-XMLHttpRequest":
        form_params = f"data.append('url', '{long_url}');"

        if alias is not None:
            form_params += f"\ndata.append('alias', '{alias}');"
        if password is not None:
            form_params += f"\ndata.append('password', '{password}');"
        if max_clicks is not None:
            form_params += f"\ndata.append('max-clicks', '{max_clicks}');"

        return (
            f"""const url = 'https://spoo.me/';
const data = new URLSearchParams();
{form_params}

const xhr = new XMLHttpRequest();
xhr.open('POST', url, true);
xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
xhr.setRequestHeader('Accept', 'application/json');

xhr.onreadystatechange = function () {{
    if (xhr.readyState == 4) {{
        if (xhr.status == 200) {{
            console.log(xhr.responseText);
        }} else {{
            console.error(`HTTP error! Status: ${{xhr.status}}`);
        }}
    }}
}};

xhr.send(data);""",
            "js",
        )

    elif language == "Kotlin":
        form_params = f"url={long_url}"

        if alias is not None:
            form_params += f"&alias={alias}"
        if password is not None:
            form_params += f"&password={password}"
        if max_clicks is not None:
            form_params += f"&max-clicks={max_clicks}"

        return (
            f"""import okhttp3.MediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody

fun main() {{
    val client = OkHttpClient()

    val mediaType = MediaType.parse("application/x-www-form-urlencoded")
    val body = RequestBody.create(mediaType, "{form_params}")

    val request = Request.Builder()
        .url("https://spoo.me/")
        .post(body)
        .addHeader("content-type", "application/x-www-form-urlencoded")
        .addHeader("Accept", "application/json")
        .build()

    // Use try-with-resources to automatically close the response
    client.newCall(request).execute().use {{ response ->
        if (!response.isSuccessful) {{
            // Handle unsuccessful response
            println("HTTP error! Status: ${{response.code()}}")
        }} else {{
            // Handle successful response
            val responseBody = response.body()?.string()
            println(responseBody)
        }}
    }}
}}""",
            "kotlin",
        )

    elif language == "Node.js-Request":
        form_params = f"url: '{long_url}'"

        if alias is not None:
            form_params += f",\n    alias: '{alias}'"
        if password is not None:
            form_params += f",\n    password: '{password}'"
        if max_clicks is not None:
            form_params += f",\n    'max-clicks': '{max_clicks}'"

        return (
            f"""const request = require('request');

const options = {{
    method: 'POST',
    url: 'https://spoo.me/',
    headers: {{
        'content-type': 'application/x-www-form-urlencoded',
        Accept: 'application/json',
    }},
    form: {{
        {form_params}
    }}
    }};

request(options, function (error, response, body) {{
    if (error) throw new Error(error);

    console.log(body);
}});""",
            "js",
        )

    elif language == "Node.js-Axios":
        form_params = f"url: '{long_url}'"

        if alias is not None:
            form_params += f",\n    alias: '{alias}'"
        if password is not None:
            form_params += f",\n    password: '{password}'"
        if max_clicks is not None:
            form_params += f",\n    'max-clicks': '{max_clicks}'"

        return (
            f"""const axios = require('axios');

const data = {{
    {form_params}
}};

axios.post('https://spoo.me/', data, {{
    headers: {{
        'content-type': 'application/x-www-form-urlencoded',
        Accept: 'application/json',
    }},
}})

.then(function (response) {{
    console.log(response.data);
}})

.catch(function (error) {{
    console.error(error);
}});""",
            "js",
        )

    elif language == "Node.js-Unirest":
        form_params = f"url: '{long_url}'"

        if alias is not None:
            form_params += f",\n    alias: '{alias}'"
        if password is not None:
            form_params += f",\n    password: '{password}'"
        if max_clicks is not None:
            form_params += f",\n    'max-clicks': '{max_clicks}'"

        return (
            f"""var unirest = require('unirest');

var req = unirest('POST', 'https://spoo.me/');
req.headers({{
    'content-type': 'application/x-www-form-urlencoded',
    Accept: 'application/json'
}})

.form({{
    {form_params}
}})

.end(function (res) {{
    if (res.error) throw new Error(res.error);

    console.log(res.body);
}});""",
            "js",
        )

    elif language == "PHP":
        form_params = f"url={long_url}"

        if alias is not None:
            form_params += f"&alias={alias}"
        if password is not None:
            form_params += f"&password={password}"
        if max_clicks is not None:
            form_params += f"&max-clicks={max_clicks}"

        return (
            f"""<?php

$curl = curl_init();

curl_setopt_array($curl, [
    CURLOPT_URL => "https://spoo.me",
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_ENCODING => "",
    CURLOPT_MAXREDIRS => 10,
    CURLOPT_TIMEOUT => 30,
    CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
    CURLOPT_CUSTOMREQUEST => "POST",
    CURLOPT_POSTFIELDS => "{form_params}",
    CURLOPT_HTTPHEADER => [
        "Accept: application/json",
        "content-type: application/x-www-form-urlencoded"
    ],
]);

$response = curl_exec($curl);
$err = curl_error($curl);

curl_close($curl);

if ($err) {{
    echo "cURL Error #:" . $err;
}} else {{
    echo $response;
}}""",
            "php",
        )

    elif language == "R":
        form_params = f"url={long_url}"

        if alias is not None:
            form_params += f"&alias={alias}"
        if password is not None:
            form_params += f"&password={password}"
        if max_clicks is not None:
            form_params += f"&max-clicks={max_clicks}"

        return (
            f"""library(httr)

url <- "https://spoo.me"

payload <- "{form_params}"

encode <- "form"

tryCatch({{
    response <- VERB("POST", url,
                body = payload,
                content_type("application/x-www-form-urlencoded"),
                accept("application/json"),
                encode = encode)

    content(response, "text")
}}, error = function(e) {{
    cat("Error: ", conditionMessage(e), "\\n")
}})""",
            "r",
        )

    elif language == "Ruby":
        form_params = f"url={long_url}"

        if alias is not None:
            form_params += f"&alias={alias}"
        if password is not None:
            form_params += f"&password={password}"
        if max_clicks is not None:
            form_params += f"&max-clicks={max_clicks}"

        return (
            f"""require 'uri'
require 'net/http'

url = URI("https://spoo.me")

http = Net::HTTP.new(url.host, url.port)
http.use_ssl = true

request = Net::HTTP::Post.new(url)
request["content-type"] = 'application/x-www-form-urlencoded'
request["Accept"] = 'application/json'
request.body = "{form_params}"

response = http.request(request)
puts response.read_body""",
            "ruby",
        )

    elif language == "Shell":
        form_params = f"url={long_url}"

        if alias is not None:
            form_params += f"&alias={alias}"
        if password is not None:
            form_params += f"&password={password}"
        if max_clicks is not None:
            form_params += f"&max-clicks={max_clicks}"

        return (
            f"""curl -X POST "https://spoo.me/" -H "Accept: application/json" -d "{form_params}" """,
            "shell",
        )

    elif language == "Rust":
        form_params = f"""
        params.insert("url", "{long_url}");
        """

        if alias is not None:
            form_params += f'params.insert("alias", "{alias}");\n        '
        if password is not None:
            form_params += f'params.insert("password", "{password}");\n        '
        if max_clicks is not None:
            form_params += f'params.insert("max-clicks", "{max_clicks}");\n        '

        return (
            f"""use reqwest::blocking::Client;
use std::collections::HashMap;

fn main() {{
    let url = "https://spoo.me/";

    let mut params = HashMap::new();
    {form_params}
    let client = Client::new();

    match client.post(url)
        .form(&params)
        .header("Accept", "application/json")
        .send()
    {{
        Ok(response) => {{
            if response.status().is_success() {{
                match response.text() {{
                    Ok(body) => println!("{{}}", body),
                    Err(err) => eprintln!("Error reading response body: {{}}", err),
                }}
            }} else {{
                eprintln!("HTTP request failed with status code: {{}}", response.status());
            }}
        }}
        Err(err) => eprintln!("HTTP request error: {{}}", err),
    }}
}}""",
            "rust",
        )


def validate_password(password):
    # Check if the password is at least 8 characters long
    if len(password) < 8:
        return False

    # Check if the password contains a letter, a number, and the allowed special characters
    if not re.search(r"[a-zA-Z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[@.]", password):
        return False

    # Check if there are consecutive special characters
    if re.search(r"[@.]{2}", password):
        return False

    return True


def validate_url(url):
    pattern = re.compile(
        r"^(https?:\/\/)?(www\.)?[a-zA-Z0-9]+([\-\.]{1}[a-zA-Z0-9]+)*\.[a-zA-Z]{2,6}(\:[0-9]{1,5})?(\/.*)?$"
    )

    if "spoo.me" in url:
        return False

    if re.fullmatch(pattern, url):
        return True
    else:
        return False


def validate_string(string):
    pattern = r"^[a-zA-Z0-9_-]*$"
    return bool(re.search(pattern, string))
