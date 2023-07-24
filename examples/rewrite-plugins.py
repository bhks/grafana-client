import json

def remove_key_from_objects(json_data, key_to_remove):
    for obj in json_data:
        if key_to_remove in obj:
            del obj[key_to_remove]

def write_json_to_file(json_data, output_file):
    with open(output_file, 'w') as file:
        json.dump(json_data, file, indent=4)

if __name__ == "__main__":
    input_file_path = "plugin-build-manifest.json"      # Replace with the path to your input JSON file
    output_file_path = "plugin-build-manifest-v3.json"    # Replace with the path for the output JSON file
    key_to_remove = "s3Uri"     # Replace with the key you want to remove from objects

    try:
        with open(input_file_path, 'r') as input_file:
            json_data = json.load(input_file)

        #remove_key_from_objects(json_data["plugins"]["versions"], key_to_remove)
        items = []
        for plugin in json_data["plugins"]["versions"]:
            items.append(plugin["name"])

        itemString = ",".join(items)
        write_json_to_file(itemString, output_file_path)
        print(f"The key '{key_to_remove}' has been removed from the objects and written to '{output_file_path}'.")
    except FileNotFoundError:
        print(f"File not found at: {input_file_path}")
    except json.JSONDecodeError:
        print("Error while parsing JSON data from the file.")
    except Exception as e:
        print(f"An error occurred: {e}")
