import os
import base64
from io import BytesIO
from PIL import Image
from openai import OpenAI
from flask import current_app

class ImageAnalyzer:
    def __init__(self):
        self.client = OpenAI(api_key=current_app.config['OPENAI_API_KEY'])
    
    def encode_image(self, image_path):
        """Encode image to base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_prescription_image(self, image_path):
        """
        Analyze prescription image and extract medication information
        Returns a dictionary with extracted data
        """
        try:
            base64_image = self.encode_image(image_path)
            
            response = self.client.chat.completions.create(
                model="gpt-4o",  # or "gpt-4-vision-preview"
                messages=[
                    {
                        "role": "system",
                        "content": """You are a medical prescription analyzer. Extract medication information from prescription images.
                        Return ONLY a valid JSON object with this exact structure (no markdown, no extra text):
                        {
                            "name": "medication name",
                            "generic_name": "generic/scientific name if visible",
                            "brand_name": "brand name if different from name",
                            "dosage": "dosage amount (e.g., 400 mg)",
                            "frequency": "how often to take (e.g., twice daily, every 8 hours)",
                            "instructions": "doctor's instructions",
                            "notes": "any additional notes",
                            "manufacturer": "manufacturer name if visible",
                            "strength": "strength/concentration",
                            "route_of_administration": "how to take it (oral, topical, etc.)"
                        }
                        
                        If any field is not clearly visible or uncertain, use null for that field.
                        Be conservative - only include information you're confident about."""
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Please analyze this prescription image and extract all medication information. Return only the JSON object, no other text."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.1,  # Low temperature for more consistent results
            )
            
            # Extract the response content
            content = response.choices[0].message.content
            
            # Parse JSON from response
            import json
            
            # Clean the response (remove markdown code blocks if present)
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            medication_data = json.loads(content)
            
            return {
                'success': True,
                'data': medication_data,
                'confidence': 'high' if len([v for v in medication_data.values() if v]) > 5 else 'medium'
            }
            
        except json.JSONDecodeError as e:
            current_app.logger.error(f"JSON parsing error: {str(e)}")
            current_app.logger.error(f"Raw response: {content}")
            return {
                'success': False,
                'error': 'Could not parse medication information from image',
                'details': str(e)
            }
        except Exception as e:
            current_app.logger.error(f"Image analysis error: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to analyze image',
                'details': str(e)
            }
    
    def validate_image(self, file_path):
        """Validate that the file is a valid image"""
        try:
            img = Image.open(file_path)
            img.verify()
            return True
        except Exception:
            return False
