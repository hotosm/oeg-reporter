import copy

from server.models.serializers.document import DocumentSchema


def update_document(document: dict, update_fields: dict) -> dict:
    """
    """
    updated_document = copy.deepcopy(document)
    for key in update_fields.keys():
        for nested_key, value in update_fields[key].items():
            if isinstance(update_fields[key][nested_key], list):
                updated_document[key][nested_key] = list(value)
            elif isinstance(update_fields[key][nested_key], dict):
                for nested_dict_key in update_fields[key][nested_key]:
                    updated_document[key][nested_key][nested_dict_key] = update_fields[
                        key
                    ][nested_key][nested_dict_key]
            else:
                updated_document[key][nested_key] = value

    # validate schema
    document_schema = DocumentSchema(partial=True)
    document = document_schema.load(updated_document)

    return updated_document
