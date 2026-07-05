#!/usr/bin/env python3
import argparse
import sys


def convert_utf8_to_ascii(input_path, output_path, error_mode):
    try:
        # Read the UTF-8 file
        with open(input_path, "r", encoding="utf-8") as infile:
            content = infile.read()

        # Write the ASCII file using the chosen error handling mode
        with open(output_path, "w", encoding="ascii", errors=error_mode) as outfile:
            outfile.write(content)

        print(
            f"Success: Converted '{input_path}' to '{output_path}' (Mode: {error_mode})"
        )

    except FileNotFoundError:
        print(f"Error: The file '{input_path}' does not exist.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Convert a UTF-8 encoded text file to ASCII."
    )

    # Positional arguments for input and output files
    parser.add_argument("input_file", help="Path to the source UTF-8 file")
    parser.add_argument("output_file", help="Path to save the target ASCII file")

    # Optional argument to control how non-ASCII characters are handled
    parser.add_argument(
        "--mode",
        choices=["ignore", "replace", "xmlcharrefreplace"],
        default="ignore",
        help="How to handle non-ASCII characters. 'ignore' drops them (default), 'replace' turns them to '?', 'xmlcharrefreplace' keeps them as XML entities.",
    )

    args = parser.parse_args()

    convert_utf8_to_ascii(args.input_file, args.output_file, args.mode)


if __name__ == "__main__":
    main()

