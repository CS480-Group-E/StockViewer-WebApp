#!/bin/bash
# deletes /* comments */ from CSS file since GPT includes so many redundantly.

input_file="$1"

if [[ -z "$input_file" || ! -f "$input_file" ]]; then
    echo "Error: Input file not found."
    echo "Usage: $0 input_file.css"
    exit 1
fi

temp_file=$(mktemp)

# Remove single-line CSS comments
sed 's|/\*[^*]*\*/||g' "$input_file" > "$temp_file"

mv "$temp_file" "$input_file"

echo "Comments removed from $input_file"
