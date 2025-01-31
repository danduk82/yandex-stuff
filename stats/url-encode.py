#!/usr/bin/env python3
import sys
import urllib.parse

def encode_urls(input_file, output_file=None):
    try:
        with open(input_file, "r") as infile:
            lines = infile.readlines()

        encoded_urls = []
        for line in lines:
            url = line.strip()
            if not url:
                continue

            # Parse URL into components
            parsed_url = urllib.parse.urlsplit(url)

            # Re-encode query parameters
            query_params = urllib.parse.parse_qsl(parsed_url.query, keep_blank_values=True)
            encoded_query = urllib.parse.urlencode(query_params, safe=":/")

            # Reconstruct the URL with encoded query parameters
            encoded_url = urllib.parse.urlunsplit((
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path,
                encoded_query,
                parsed_url.fragment
            ))

            encoded_urls.append(encoded_url)

        # Write to file or stdout
        if output_file:
            with open(output_file, "w") as outfile:
                outfile.write("\n".join(encoded_urls) + "\n")
            print(f"Encoded URLs saved to {output_file}")
        else:
            for url in encoded_urls:
                print(url)

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python encode_urls.py <input_file> [output_file]", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    encode_urls(input_file, output_file)
