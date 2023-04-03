from docxtpl import DocxTemplate

def create_document(doc_type, contractor, groups):
    contract = DocxTemplate(doc_type.template)
    context = { 
        'contractor_name' : contractor.name, 
        'groups' : groups
        }
    contract.render(context)
    path_to_contract = f'media/documents/contract.docx' 
    contract.save(path_to_contract)
    
    return contract