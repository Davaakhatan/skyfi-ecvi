"""AI/ML service for data collection and verification using LangChain and agentic systems"""

from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import datetime
import logging
import json

from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    from langchain.agents import AgentExecutor, create_openai_tools_agent
    from langchain_openai import ChatOpenAI
    from langchain_anthropic import ChatAnthropic
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain.tools import Tool
    from langchain_core.messages import HumanMessage, AIMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.warning("LangChain not available - AI features will be disabled")


class LLMClient:
    """LLM client wrapper for OpenAI and Anthropic"""
    
    def __init__(self, provider: str = None):
        self.provider = provider or settings.LLM_PROVIDER.lower()
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize LLM based on provider"""
        if self.provider == "openai":
            if not settings.OPENAI_API_KEY:
                logger.warning("OpenAI API key not set, LLM features will be disabled")
                return None
            return ChatOpenAI(
                model="gpt-4-turbo-preview",
                temperature=0.1,
                api_key=settings.OPENAI_API_KEY
            )
        elif self.provider == "anthropic":
            if not settings.ANTHROPIC_API_KEY:
                logger.warning("Anthropic API key not set, LLM features will be disabled")
                return None
            return ChatAnthropic(
                model="claude-3-opus-20240229",
                temperature=0.1,
                api_key=settings.ANTHROPIC_API_KEY
            )
        else:
            logger.warning(f"Unknown LLM provider: {self.provider}")
            return None
    
    def is_available(self) -> bool:
        """Check if LLM is available"""
        return self.llm is not None
    
    def invoke(self, prompt: str, **kwargs) -> Optional[str]:
        """Invoke LLM with prompt"""
        if not self.is_available():
            return None
        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"LLM invocation failed: {e}")
            return None


class CompanyResearcherAgent:
    """Agent for researching company information from multiple sources"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.tools = self._create_tools()
        self.agent = self._create_agent()
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the researcher agent"""
        tools = [
            Tool(
                name="web_search",
                func=self._web_search,
                description="Search the web for company information. Input should be a search query string."
            ),
            Tool(
                name="api_lookup",
                func=self._api_lookup,
                description="Look up company data from public APIs. Input should be company name and registration number."
            ),
            Tool(
                name="extract_data",
                func=self._extract_data,
                description="Extract structured data from unstructured text. Input should be the text to extract from."
            ),
        ]
        return tools
    
    def _web_search(self, query: str) -> str:
        """Web search tool with web scraping support"""
        try:
            from app.services.web_scraper import WebScraper
            scraper = WebScraper()
            
            # For now, use web scraping to search
            # TODO: Integrate with actual search API (SerpAPI, Google Custom Search) for better results
            logger.info(f"Web search query: {query}")
            
            # Try to construct a search URL (this is a placeholder)
            # In production, use a proper search API
            search_results = scraper.search_company_info(query)
            
            return json.dumps({
                "query": query,
                "results": search_results,
                "note": "Using web scraping. Consider integrating with search APIs for better results."
            })
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return json.dumps({"error": str(e), "query": query})
    
    def _api_lookup(self, input_str: str) -> str:
        """API lookup tool for company registry APIs"""
        try:
            from app.services.data_collection import DataCollectionService
            
            # Parse input (expects JSON string with company info)
            try:
                params = json.loads(input_str) if input_str.startswith("{") else {"query": input_str}
            except json.JSONDecodeError:
                params = {"query": input_str}
            
            company_name = params.get("company_name") or params.get("query", "")
            registration_number = params.get("registration_number")
            jurisdiction = params.get("jurisdiction")
            
            # Use DataCollectionService for API lookups
            collection_service = DataCollectionService()
            
            # Configure sources based on jurisdiction
            sources = []
            
            # UK Companies House
            if jurisdiction and jurisdiction.upper() in ["GB", "UK", "GBR"]:
                sources.append({
                    "name": "companies_house_uk",
                    "type": "api",
                    "endpoint": "https://api.company-information.service.gov.uk/company",
                    "params": {
                        "q": company_name
                    },
                    "headers": {
                        "Authorization": f"Basic {settings.COMPANY_REGISTRY_API_KEY}" if settings.COMPANY_REGISTRY_API_KEY else None
                    },
                    "use_cache": True
                })
            
            # US SEC EDGAR
            if jurisdiction and jurisdiction.upper() in ["US", "USA"]:
                sources.append({
                    "name": "sec_edgar",
                    "type": "api",
                    "endpoint": "https://www.sec.gov/cgi-bin/browse-edgar",
                    "params": {
                        "company": company_name,
                        "action": "getcompany"
                    },
                    "headers": {
                        "User-Agent": "ECVI-Bot/1.0"
                    },
                    "use_cache": True
                })
            
            if sources:
                result = collection_service.collect_from_multiple_sources(sources, company_name)
                return json.dumps(result)
            else:
                return json.dumps({
                    "success": False,
                    "error": f"No API sources configured for jurisdiction: {jurisdiction}",
                    "input": input_str
                })
                
        except Exception as e:
            logger.error(f"API lookup failed: {e}")
            return json.dumps({"error": str(e), "input": input_str})
    
    def _extract_data(self, input_str: str) -> str:
        """Extract structured data from text or HTML using LLM and web scraping"""
        
        # Check if input is HTML or plain text
        is_html = "<html" in input_str.lower() or "<body" in input_str.lower()
        
        if is_html:
            # Use web scraper for HTML extraction
            try:
                from app.services.web_scraper import WebScraper
                scraper = WebScraper()
                extraction_result = scraper.extract_company_data(input_str)
                
                if extraction_result.get("success"):
                    return json.dumps(extraction_result.get("extracted_data", {}))
            except Exception as e:
                logger.warning(f"Web scraper extraction failed, falling back to LLM: {e}")
        
        # Use LLM for text extraction
        if not self.llm_client.is_available():
            return json.dumps({"error": "LLM not available for data extraction"})
        
        prompt = f"""Extract structured company information from the following text.
        Return a JSON object with fields: legal_name, registration_number, jurisdiction, 
        domain, address, email, phone, website.
        
        Text: {input_str[:2000]}  # Limit text length
        
        Return only valid JSON, no additional text."""
        
        result = self.llm_client.invoke(prompt)
        if result:
            try:
                # Try to parse as JSON to validate
                json.loads(result)
                return result
            except json.JSONDecodeError:
                # If not valid JSON, wrap it
                return json.dumps({"extracted_text": result})
        
        return json.dumps({"error": "Failed to extract data"})
    
    def _create_agent(self) -> Optional[AgentExecutor]:
        """Create the researcher agent"""
        if not LANGCHAIN_AVAILABLE:
            logger.warning("LangChain not available - agent creation skipped")
            return None
        if not self.llm_client.is_available():
            return None
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a company research agent. Your task is to collect comprehensive 
            information about companies from multiple sources. Use the available tools to:
            1. Search the web for company information
            2. Look up data from public APIs
            3. Extract structured data from unstructured text
            
            Always verify information from multiple sources and note the source of each data point.
            Return structured data in JSON format."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        try:
            agent = create_openai_tools_agent(
                self.llm_client.llm,
                self.tools,
                prompt
            )
            return AgentExecutor(agent=agent, tools=self.tools, verbose=True)
        except Exception as e:
            logger.error(f"Failed to create researcher agent: {e}")
            return None
    
    def research_company(
        self,
        legal_name: str,
        registration_number: Optional[str] = None,
        domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Research company information from multiple sources
        
        Args:
            legal_name: Company legal name
            registration_number: Optional registration number
            domain: Optional company domain
        
        Returns:
            Dictionary with collected company data
        """
        if not self.agent:
            return {
                "error": "Agent not available - LLM not configured",
                "data": {}
            }
        
        query = f"Research company: {legal_name}"
        if registration_number:
            query += f", Registration: {registration_number}"
        if domain:
            query += f", Domain: {domain}"
        
        try:
            result = self.agent.invoke({"input": query})
            return {
                "success": True,
                "data": result.get("output", ""),
                "sources": []  # TODO: Track sources
            }
        except Exception as e:
            logger.error(f"Company research failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": {}
            }


class DataVerifierAgent:
    """Agent for verifying and cross-referencing collected data"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.tools = self._create_tools()
        self.agent = self._create_agent()
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the verifier agent"""
        tools = [
            Tool(
                name="cross_reference",
                func=self._cross_reference,
                description="Cross-reference data from multiple sources. Input should be JSON with data from different sources."
            ),
            Tool(
                name="dns_verify",
                func=self._dns_verify,
                description="Verify DNS records for a domain. Input should be a domain name."
            ),
            Tool(
                name="validate_format",
                func=self._validate_format,
                description="Validate data format (email, phone, address, etc.). Input should be the field name and value."
            ),
        ]
        return tools
    
    def _cross_reference(self, input_str: str) -> str:
        """Cross-reference data from multiple sources"""
        # TODO: Implement cross-referencing logic
        logger.info(f"Cross-referencing: {input_str}")
        return f"Cross-reference results: {input_str} (placeholder)"
    
    def _dns_verify(self, domain: str) -> str:
        """DNS verification tool"""
        try:
            from app.services.dns_verification import DNSVerificationService
            dns_service = DNSVerificationService()
            
            # Perform DNS verification
            dns_result = dns_service.verify_domain(domain)
            
            # Format results as JSON string
            return json.dumps({
                "domain": domain,
                "verified": dns_result.get("verified", False),
                "a_records": dns_result.get("a_records", []),
                "mx_records": dns_result.get("mx_records", []),
                "ns_records": dns_result.get("ns_records", []),
                "domain_age_days": dns_result.get("domain_age_days"),
                "ssl_valid": dns_result.get("ssl_valid", False),
                "domain_matches_company": dns_result.get("domain_matches_company", False)
            })
        except Exception as e:
            logger.error(f"DNS verification failed: {e}")
            return json.dumps({"error": str(e), "domain": domain})
    
    def _validate_format(self, input_str: str) -> str:
        """Validate data format"""
        # TODO: Implement format validation
        logger.info(f"Format validation: {input_str}")
        return f"Validation results: {input_str} (placeholder)"
    
    def _create_agent(self) -> Optional[AgentExecutor]:
        """Create the verifier agent"""
        if not LANGCHAIN_AVAILABLE:
            logger.warning("LangChain not available - agent creation skipped")
            return None
        if not self.llm_client.is_available():
            return None
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a data verification agent. Your task is to:
            1. Cross-reference data from multiple sources
            2. Verify DNS records and domain information
            3. Validate data formats (email, phone, address)
            4. Identify discrepancies and inconsistencies
            5. Calculate confidence scores for each data point
            
            Return structured verification results in JSON format."""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        try:
            agent = create_openai_tools_agent(
                self.llm_client.llm,
                self.tools,
                prompt
            )
            return AgentExecutor(agent=agent, tools=self.tools, verbose=True)
        except Exception as e:
            logger.error(f"Failed to create verifier agent: {e}")
            return None
    
    def verify_data(self, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify and cross-reference collected data
        
        Args:
            collected_data: Dictionary with collected company data
        
        Returns:
            Dictionary with verification results
        """
        if not self.agent:
            return {
                "error": "Agent not available - LLM not configured",
                "verified_data": {}
            }
        
        # Convert collected_data to string if it's a dict to avoid serialization issues
        if isinstance(collected_data, dict):
            query = f"Verify and cross-reference the following company data: {json.dumps(collected_data, default=str)}"
        else:
            query = f"Verify and cross-reference the following company data: {collected_data}"
        
        try:
            result = self.agent.invoke({"input": query})
            return {
                "success": True,
                "verified_data": result.get("output", ""),
                "confidence_scores": {},
                "discrepancies": []
            }
        except Exception as e:
            logger.error(f"Data verification failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "verified_data": {}
            }


class AIOrchestrator:
    """Orchestrator for coordinating AI agents in the verification process"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.researcher_agent = CompanyResearcherAgent(self.llm_client)
        self.verifier_agent = DataVerifierAgent(self.llm_client)
    
    def collect_company_data(
        self,
        legal_name: str,
        registration_number: Optional[str] = None,
        domain: Optional[str] = None,
        jurisdiction: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Collect company data using AI agents
        
        Args:
            legal_name: Company legal name
            registration_number: Optional registration number
            domain: Optional company domain
            jurisdiction: Optional jurisdiction code
        
        Returns:
            Dictionary with collected and verified company data
        """
        logger.info(f"Starting AI data collection for company: {legal_name}")
        
        # Step 1: Research company information
        research_result = self.researcher_agent.research_company(
            legal_name=legal_name,
            registration_number=registration_number,
            domain=domain
        )
        
        if not research_result.get("success"):
            return {
                "success": False,
                "error": research_result.get("error", "Research failed"),
                "collected_data": {},
                "verified_data": {}
            }
        
        # Step 2: Verify collected data
        collected_data = research_result.get("data", {})
        verification_result = self.verifier_agent.verify_data(collected_data)
        
        return {
            "success": True,
            "collected_data": collected_data,
            "verified_data": verification_result.get("verified_data", {}),
            "confidence_scores": verification_result.get("confidence_scores", {}),
            "discrepancies": verification_result.get("discrepancies", []),
            "sources": research_result.get("sources", [])
        }
    
    def is_available(self) -> bool:
        """Check if AI services are available"""
        return self.llm_client.is_available()

