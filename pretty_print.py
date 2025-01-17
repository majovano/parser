import json
from datetime import datetime
from typing import List, Dict


class ReleaseNote:
    def __init__(self, title: str, description: str):
        self.title = title
        self.description = description

    def __repr__(self) -> str:
        return f"ReleaseNote(title='{self.title}')"

    def to_dict(self) -> Dict:
        return {
            'title': self.title,
            'description': self.description
        }


def parse_release_notes(json_data: str) -> List[ReleaseNote]:
    """
    Parse the JSON string into a list of ReleaseNote objects

    Args:
        json_data (str): JSON string containing release notes

    Returns:
        List[ReleaseNote]: List of parsed ReleaseNote objects
    """
    try:
        # Parse JSON string into Python object
        data = json.loads(json_data)

        # Create ReleaseNote objects from the data
        release_notes = [ReleaseNote(item['title'], item['description'])
                         for item in data]

        return release_notes

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []
    except KeyError as e:
        print(f"Missing required key in JSON data: {e}")
        return []


def serialize_to_json(release_notes: List[ReleaseNote], output_file: str) -> None:
    """
    Serialize ReleaseNote objects to a JSON file

    Args:
        release_notes (List[ReleaseNote]): List of ReleaseNote objects to serialize
        output_file (str): Path to output JSON file
    """
    try:
        # Convert ReleaseNote objects to dictionaries
        data = [note.to_dict() for note in release_notes]

        # Write to JSON file with proper formatting
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Successfully wrote {len(release_notes)} release notes to {output_file}")

    except IOError as e:
        print(f"Error writing to file: {e}")
    except Exception as e:
        print(f"Unexpected error during serialization: {e}")


def analyze_release_notes(release_notes: List[ReleaseNote]) -> Dict:
    """
    Perform basic analysis on the release notes

    Args:
        release_notes (List[ReleaseNote]): List of ReleaseNote objects to analyze

    Returns:
        Dict: Analysis results
    """
    return {
        'total_notes': len(release_notes),
        'avg_title_length': sum(len(note.title) for note in release_notes) / len(release_notes),
        'avg_description_length': sum(len(note.description) for note in release_notes) / len(release_notes)
    }


# Example usage
if __name__ == "__main__":
    # Read the JSON content from file
    with open('paste.txt', 'r', encoding='utf-8') as f:
        json_content = f.read()

    # Parse the release notes
    release_notes = parse_release_notes(json_content)

    # Analyze the data
    analysis = analyze_release_notes(release_notes)
    print("\nAnalysis Results:")
    print(f"Total number of release notes: {analysis['total_notes']}")
    print(f"Average title length: {analysis['avg_title_length']:.2f} characters")
    print(f"Average description length: {analysis['avg_description_length']:.2f} characters")

    # Serialize to a new JSON file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"release_notes_{timestamp}.json"
    serialize_to_json(release_notes, output_file)