"""
AI service for generating content suggestions using AWS Bedrock.
"""

import json
import boto3
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError
import streamlit as st

from config import settings


class AIService:
    """Service for AI-powered content enhancement using AWS Bedrock."""

    def __init__(self):
        """Initialize the AI service."""
        self.region = settings.AWS_REGION
        self.model_id = settings.BEDROCK_MODEL_ID
        self.client = None

    def _get_bedrock_client(self):
        """Get or create Bedrock runtime client."""
        if self.client is None:
            try:
                self.client = boto3.client(
                    service_name='bedrock-runtime',
                    region_name=self.region,
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                )
            except Exception as e:
                st.error(f"Failed to initialize AWS Bedrock client: {str(e)}")
                raise

        return self.client

    def format_prompt(self, submission_data: Dict[str, str]) -> str:
        """
        Format the prompt for AI suggestion generation.

        Args:
            submission_data: Dictionary containing submission fields

        Returns:
            Formatted prompt string
        """
        return settings.AI_PROMPT_TEMPLATE.format(
            project_name=submission_data.get('project_name', 'N/A'),
            title=submission_data.get('title', ''),
            description=submission_data.get('description', ''),
            key_achievements=submission_data.get('key_achievements', ''),
            impact=submission_data.get('impact', ''),
            category=submission_data.get('category', 'N/A')
        )

    def generate_suggestions(self, submission_data: Dict[str, str]) -> Optional[Dict[str, str]]:
        """
        Generate AI-powered suggestions for submission content.

        Args:
            submission_data: Dictionary containing submission fields

        Returns:
            Dictionary with suggested improvements or None if generation failed
        """
        try:
            client = self._get_bedrock_client()
            prompt = self.format_prompt(submission_data)

            # Prepare the request body for Claude
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,
                "temperature": 0.7,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }

            # Invoke the model
            response = client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )

            # Parse the response
            response_body = json.loads(response['body'].read())

            # Extract the content from Claude's response
            if 'content' in response_body and len(response_body['content']) > 0:
                content = response_body['content'][0]['text']

                # Try to parse as JSON
                try:
                    suggestions = json.loads(content)
                    return suggestions
                except json.JSONDecodeError:
                    # If not JSON, try to extract JSON from the content
                    import re
                    json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
                    if json_match:
                        suggestions = json.loads(json_match.group())
                        return suggestions
                    else:
                        st.error("Failed to parse AI suggestions as JSON")
                        return None
            else:
                st.error("No content in AI response")
                return None

        except ClientError as e:
            st.error(f"AWS Bedrock API error: {str(e)}")
            return None
        except Exception as e:
            st.error(f"Error generating AI suggestions: {str(e)}")
            return None

    def generate_suggestions_with_retry(self, submission_data: Dict[str, str],
                                       max_retries: int = 3) -> Optional[Dict[str, str]]:
        """
        Generate AI suggestions with retry logic.

        Args:
            submission_data: Dictionary containing submission fields
            max_retries: Maximum number of retry attempts

        Returns:
            Dictionary with suggested improvements or None if all retries failed
        """
        for attempt in range(max_retries):
            try:
                result = self.generate_suggestions(submission_data)
                if result:
                    return result
            except Exception as e:
                if attempt == max_retries - 1:
                    st.error(f"Failed after {max_retries} attempts: {str(e)}")
                    return None
                else:
                    st.warning(f"Attempt {attempt + 1} failed, retrying...")

        return None


def test_bedrock_connection() -> bool:
    """
    Test connection to AWS Bedrock.

    Returns:
        True if connection is successful, False otherwise
    """
    try:
        ai_service = AIService()
        client = ai_service._get_bedrock_client()

        # Try to list available models as a connectivity test
        # Note: This requires appropriate IAM permissions
        test_data = {
            'project_name': 'Test Project',
            'title': 'Test Title',
            'description': 'Test description',
            'key_achievements': 'Test achievements',
            'impact': 'Test impact',
            'category': 'Test'
        }

        # Just test if we can create the prompt without actually calling the API
        prompt = ai_service.format_prompt(test_data)

        if prompt:
            return True

    except Exception as e:
        st.error(f"Bedrock connection test failed: {str(e)}")
        return False

    return False


def generate_mock_suggestions(submission_data: Dict[str, str]) -> Dict[str, str]:
    """
    Generate mock suggestions for testing without AWS Bedrock.

    Args:
        submission_data: Dictionary containing submission fields

    Returns:
        Dictionary with mock suggested improvements
    """
    return {
        'title': f"Enhanced: {submission_data.get('title', 'Untitled')}",
        'description': f"[Enhanced] {submission_data.get('description', '')} This improved description provides more context and clarity.",
        'key_achievements': f"Key highlights: {submission_data.get('key_achievements', '')} These achievements demonstrate significant impact.",
        'impact': f"Measurable results: {submission_data.get('impact', '')} This represents substantial value to the organization."
    }


# Singleton instance
_ai_service_instance = None


def get_ai_service() -> AIService:
    """
    Get the singleton AI service instance.

    Returns:
        AIService instance
    """
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    return _ai_service_instance
