import http.server
import socketserver
from urllib.parse import parse_qs
from datetime import datetime
import json

PORT = 8000

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/static/index.html'
        else:
            self.path = f'/static{self.path}'

        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == '/submit':
            # Get the length of the data
            content_length = int(self.headers['Content-Length'])
            # Read the data
            post_data = self.rfile.read(content_length)
            # Parse the form data
            form_data = parse_qs(post_data.decode('utf-8'))

            first_name = form_data.get('first_name', [''])[0]
            last_name = form_data.get('last_name', [''])[0]

            # Side effect is saving to the database
            timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            json_object = {"firstName":first_name,"lastName":last_name}
            with open(f'database/submission-{timestamp}.json', 'w') as file:
              json.dump(json_object, file, indent=4)

            # Generate response HTML
            response = f"""
            <html>
            <body>
                <h1>Form Submitted</h1>
                <p>First Name: {first_name}</p>
                <p>Last Name: {last_name}</p>
                <a href="/">Go back to the form</a>
            </body>
            </html>
            """

            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(response.encode('utf-8'))
        else:
            # Handle other POST paths, if any
            self.send_error(404, "File Not Found")

# Set up the handler
handler = MyHttpRequestHandler

# Create an HTTP server
with socketserver.TCPServer(("", PORT), handler) as httpd:
    print(f"Serving on port {PORT}")
    httpd.serve_forever()
