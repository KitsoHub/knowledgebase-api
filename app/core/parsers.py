from rest_framework.parsers import MultiPartParser
import json


class NestedMultipartParser(MultiPartParser):
    """
    Custom parser that correctly handles nested fields in multipart requests.

    Key improvements:
    1. Properly builds nested structures even with single fields
    2. Handles metadata sent as JSON string
    3. Converts boolean strings to actual booleans
    4. Works with both flattened fields and direct JSON objects
    """

    def parse(self, stream, media_type=None, parser_context=None):
        # First, let the default parser handle the request
        result = super().parse(stream, media_type, parser_context)
        data = result.data
        files = result.files
        parsed_data = {}

        # Process all non-file data to rebuild nested structure
        for key, value in data.lists():
            # Skip if this is actually a file field
            if key in files:
                continue

            # Handle single vs multiple values
            value = value[0] if len(value) == 1 else value

            # Process nested fields
            if '.' in key:
                self._set_nested_value(parsed_data, key, value)
            else:
                parsed_data[key] = value

        # Process file data separately
        for key in files:
            # Handle multiple files for the same field
            parsed_data[key] = files.getlist(key)

        # Handle metadata as JSON string (if sent that way)
        if 'metadata' in parsed_data and isinstance(parsed_data['metadata'], str):
            try:
                # Try to parse as JSON
                metadata_dict = json.loads(parsed_data['metadata'])
                if isinstance(metadata_dict, dict):
                    parsed_data['metadata'] = metadata_dict
            except json.JSONDecodeError:
                # Not valid JSON, leave as is for validation to handle
                pass

        # Convert boolean strings in metadata
        if 'metadata' in parsed_data and isinstance(parsed_data['metadata'], dict):
            self._convert_metadata_booleans(parsed_data['metadata'])

        result.data = parsed_data
        return result

    def _set_nested_value(self, target, path, value):
        """
        Safely set nested values in a dictionary
        Ensures all intermediate levels are dictionaries
        """
        parts = path.split('.')
        current = target

        # Build the nested structure, ensuring each level is a dict
        for i, part in enumerate(parts):
            # If we're at the last part, set the value
            if i == len(parts) - 1:
                current[part] = value
                break

            # Ensure current level is a dict
            if part not in current:
                current[part] = {}
            elif not isinstance(current[part], dict):
                # If existing value is not a dict, convert it to one
                current[part] = {'value': current[part]}

            current = current[part]

    def _convert_metadata_booleans(self, metadata):
        """Convert string 'true'/'false' to booleans for metadata fields"""
        boolean_fields = ['unesco', 'undp', 'unicef']
        for field in boolean_fields:
            if field in metadata:
                if isinstance(metadata[field], str):
                    if metadata[field].strip().lower() == 'true':
                        metadata[field] = True
                    elif metadata[field].strip().lower() == 'false':
                        metadata[field] = False

# class NestedMultipartParser(MultiPartParser):
#     """
#     Custom parser that handles nested fields in multipart requests
#     Converts fields like 'metadata.sensitivity_level' into a nested structure
#     """

#     def parse(self, stream, media_type=None, parser_context=None):
#         result = super().parse(stream, media_type, parser_context)
#         data = result.data
#         nested_data = {}

#         # Process all fields to rebuild nested structure
#         for key, value in data.lists():
#             if '.' in key:
#                 parts = key.split('.')
#                 current = nested_data
#                 for part in parts[:-1]:
#                     if part not in current:
#                         current[part] = {}
#                     current = current[part]
#                 current[parts[-1]] = value[0] if len(value) == 1 else value
#             else:
#                 nested_data[key] = value[0] if len(value) == 1 else value

#         # Handle file lists properly
#         # if 'uploaded_images' in data:
#         #     nested_data['uploaded_images'] = data.getlist('uploaded_images')

#         result.data = nested_data
#         return result
