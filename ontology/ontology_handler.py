from owlready2 import *

class OntologyHandler:
    def __init__(self, ontology_path):
        self.onto = get_ontology("/Users/kavy/KBQA_Healthcare/data/medical_ontology.owl").load()


    def get_treatment_for_disease(self, disease_name):
        """
        Fetches the treatment from the ontology.
        """
        disease = self.onto.search_one(iri=f"*{disease_name.replace(' ', '_')}*")
        if disease and hasattr(disease, "hasTreatment"):
            treatments = [t.name.replace("_", " ") for t in disease.hasTreatment]
            return f"Treatments for {disease_name}: {', '.join(treatments)}"
        return f"No treatment found for {disease_name} in the ontology."

# Example usage
if __name__ == "__main__":
    handler = OntologyHandler("../data/medical_ontology.owl")
    print(handler.get_treatment_for_disease("Diabetes"))
