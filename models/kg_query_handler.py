from owlready2 import get_ontology, sync_reasoner
import owlready2
import logging
import os
import re

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Suppress Owlready2 logging
owlready2.JAVA_EXE = "java"
owlready2.onto_path.append("/dev/null")  # Suppress logging
logging.getLogger("owlready2").setLevel(logging.CRITICAL)  # Disable logs
os.environ["OWLREADY2_JAVA_EXE"] = "true"  # Disables Java logs

class KnowledgeBase:
    def __init__(self, ontology_path=None):
        if ontology_path is None:
            # Get the absolute path to the project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            ontology_path = os.path.join(project_root, "data", "medical_ontology.owl")
            
            logger.debug(f"Current directory: {current_dir}")
            logger.debug(f"Project root: {project_root}")
            logger.debug(f"Ontology path: {ontology_path}")
            
            # Check if file exists
            if not os.path.exists(ontology_path):
                logger.error(f"Ontology file not found at: {ontology_path}")
                raise FileNotFoundError(f"Ontology file not found at: {ontology_path}")
            
            # Check if file is readable
            if not os.access(ontology_path, os.R_OK):
                logger.error(f"Ontology file is not readable at: {ontology_path}")
                raise PermissionError(f"Ontology file is not readable at: {ontology_path}")
        
        try:
            logger.info(f"Loading ontology from: {ontology_path}")
            self.onto = get_ontology(ontology_path).load()
            logger.info("Ontology loaded successfully")
            sync_reasoner()
            logger.info("Reasoner synchronized successfully")
        except Exception as e:
            logger.error(f"Error loading ontology: {str(e)}")
            raise

    def query_ontology(self, query):
        """
        Queries the ontology for medical information.
        Example query: "What is the treatment for diabetes?"
        """
        query = query.lower().strip()
        
        # Extract disease and query type
        disease_match = re.search(r"for\s+(\w+)\b", query)
        if not disease_match:
            return "Please specify a disease in your query (e.g., 'What are the symptoms of diabetes?')"
        
        disease = disease_match.group(1).capitalize()
        
        # Determine query type
        if "symptom" in query:
            return self._get_symptoms(disease)
        elif "treatment" in query:
            return self._get_treatments(disease)
        elif "cause" in query:
            return self._get_causes(disease)
        elif "prevent" in query:
            return self._get_preventions(disease)
        elif "risk" in query:
            return self._get_risk_factors(disease)
        else:
            return "I can tell you about symptoms, treatments, causes, prevention, or risk factors. What would you like to know?"

    def _get_symptoms(self, disease):
        try:
            disease_ind = self.onto.search_one(iri=f"*{disease}")
            if disease_ind:
                symptoms = [str(s).split('#')[-1] for s in disease_ind.hasSymptom]
                if symptoms:
                    return f"Symptoms of {disease} include: {', '.join(symptoms)}"
            return f"I don't have information about symptoms for {disease}"
        except Exception as e:
            logger.error(f"Error getting symptoms: {str(e)}")
            return "Sorry, I encountered an error while processing your query."

    def _get_treatments(self, disease):
        try:
            disease_ind = self.onto.search_one(iri=f"*{disease}")
            if disease_ind:
                treatments = [str(t).split('#')[-1] for t in disease_ind.hasTreatment]
                if treatments:
                    return f"Treatments for {disease} include: {', '.join(treatments)}"
            return f"I don't have information about treatments for {disease}"
        except Exception as e:
            logger.error(f"Error getting treatments: {str(e)}")
            return "Sorry, I encountered an error while processing your query."

    def _get_causes(self, disease):
        try:
            disease_ind = self.onto.search_one(iri=f"*{disease}")
            if disease_ind:
                causes = [str(c).split('#')[-1] for c in disease_ind.hasCause]
                if causes:
                    return f"Causes of {disease} include: {', '.join(causes)}"
            return f"I don't have information about causes for {disease}"
        except Exception as e:
            logger.error(f"Error getting causes: {str(e)}")
            return "Sorry, I encountered an error while processing your query."

    def _get_preventions(self, disease):
        try:
            disease_ind = self.onto.search_one(iri=f"*{disease}")
            if disease_ind:
                preventions = [str(p).split('#')[-1] for p in disease_ind.hasPrevention]
                if preventions:
                    return f"Prevention methods for {disease} include: {', '.join(preventions)}"
            return f"I don't have information about prevention for {disease}"
        except Exception as e:
            logger.error(f"Error getting preventions: {str(e)}")
            return "Sorry, I encountered an error while processing your query."

    def _get_risk_factors(self, disease):
        try:
            disease_ind = self.onto.search_one(iri=f"*{disease}")
            if disease_ind:
                risk_factors = [str(r).split('#')[-1] for r in disease_ind.hasRiskFactor]
                if risk_factors:
                    return f"Risk factors for {disease} include: {', '.join(risk_factors)}"
            return f"I don't have information about risk factors for {disease}"
        except Exception as e:
            logger.error(f"Error getting risk factors: {str(e)}")
            return "Sorry, I encountered an error while processing your query."

# Example Usage
if __name__ == "__main__":
    kb = KnowledgeBase()
    print(kb.query_ontology("diabetes treatment"))
