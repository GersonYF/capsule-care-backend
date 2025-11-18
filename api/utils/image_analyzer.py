import os
import base64
import json
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
    
    def validate_image(self, file_path):
        """Validate that the file is a valid image"""
        try:
            img = Image.open(file_path)
            img.verify()
            return True
        except Exception:
            return False
    
    def analyze_prescription_image(self, image_path):
        """
        Analyze prescription image and extract medication information including criticality
        Returns a dictionary with extracted data
        """
        try:
            base64_image = self.encode_image(image_path)
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a medical prescription analyzer. Extract medication information from prescription images.
                        
                        CRITICALITY LEVELS:
                        - "low": Vitamins, supplements, topical treatments for minor conditions, OTC medications
                        - "medium": Antibiotics, pain relievers, medications for temporary/acute conditions
                        - "high": Medications for chronic conditions requiring consistent use (hypertension, diabetes pills, thyroid, cholesterol)
                        - "critical": Life-saving medications where missing doses is dangerous:
                          * Insulin and other diabetes injectables
                          * Anticoagulants (warfarin, apixaban, rivaroxaban)
                          * Anti-seizure medications (phenytoin, carbamazepine, valproate)
                          * Cardiac medications (digoxin, amiodarone)
                          * Immunosuppressants (cyclosporine, tacrolimus)
                          * Corticosteroids at high doses
                          * Medications for severe mental health conditions
                        
                        Return ONLY a valid JSON object with this structure (no markdown, no extra text):
                        {
                            "medications": [
                                {
                                    "name": "medication name",
                                    "generic_name": "generic/scientific name if visible",
                                    "brand_name": "brand name if different",
                                    "dosage": "dosage amount (e.g., 400 mg)",
                                    "frequency": "how often (e.g., twice daily, every 8 hours)",
                                    "instructions": "doctor's instructions",
                                    "manufacturer": "manufacturer if visible",
                                    "strength": "strength/concentration",
                                    "route_of_administration": "oral/topical/injectable/etc",
                                    "criticality": "low|medium|high|critical",
                                    "criticality_reasoning": "brief explanation of criticality level"
                                }
                            ],
                            "doctor": {
                                "name": "doctor name if visible",
                                "specialty": "specialty if visible",
                                "license": "license number if visible"
                            },
                            "prescription_date": "date if visible",
                            "notes": "any additional prescription notes"
                        }
                        
                        If any field is not clearly visible, use null. Be conservative and accurate."""
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this prescription and extract all medication information including criticality assessment. Return only valid JSON."
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
                max_tokens=2000,
                temperature=0.1,
            )
            
            content = response.choices[0].message.content
            
            # Clean response
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            elif content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            medication_data = json.loads(content)
            
            # Validate criticality levels
            valid_criticalities = ['low', 'medium', 'high', 'critical']
            if 'medications' in medication_data:
                for med in medication_data['medications']:
                    if 'criticality' not in med or med['criticality'] not in valid_criticalities:
                        med['criticality'] = 'medium'  # Default fallback
                    if 'criticality_reasoning' not in med:
                        med['criticality_reasoning'] = 'Assessment based on medication type'
            
            # Backward compatibility: if old format (single medication), convert to new format
            if 'medications' not in medication_data and 'name' in medication_data:
                old_data = medication_data.copy()
                medication_data = {
                    'medications': [old_data],
                    'doctor': {},
                    'prescription_date': None,
                    'notes': None
                }
            
            # Determine confidence
            med_count = len(medication_data.get('medications', []))
            confidence = 'high' if med_count > 0 and med_count <= 5 else 'medium' if med_count > 0 else 'low'
            
            return {
                'success': True,
                'data': medication_data,
                'confidence': confidence
            }
            
        except json.JSONDecodeError as e:
            current_app.logger.error(f"JSON parsing error: {str(e)}")
            current_app.logger.error(f"Raw response: {content if 'content' in locals() else 'N/A'}")
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
    
    def analyze_medication_image(self, image_path):
        """
        Analyze medication bottle/package image
        Returns information about the medication including criticality
        """
        try:
            base64_image = self.encode_image(image_path)
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a medication package analyzer. Extract information from medication bottles, boxes, or packages.
                        
                        CRITICALITY ASSESSMENT:
                        - "low": OTC drugs, vitamins, supplements, topical treatments
                        - "medium": Antibiotics, common pain meds, allergy medications
                        - "high": Chronic condition medications (BP, diabetes pills, thyroid)
                        - "critical": Insulin, anticoagulants, anti-seizure, cardiac meds, immunosuppressants
                        
                        Return ONLY valid JSON:
                        {
                            "name": "medication name from label",
                            "generic_name": "generic name if visible",
                            "brand_name": "brand name if different",
                            "strength": "strength (e.g., 500mg)",
                            "quantity": "quantity (e.g., 30 tablets)",
                            "manufacturer": "manufacturer name",
                            "expiration_date": "expiration date if visible",
                            "ndc_code": "NDC code if visible",
                            "lot_number": "lot number if visible",
                            "instructions": "label instructions",
                            "warnings": "warning labels if visible",
                            "criticality": "low|medium|high|critical",
                            "criticality_reasoning": "brief explanation"
                        }
                        
                        Use null for fields not visible."""
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this medication bottle/package and extract all information. Return only JSON."
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
                temperature=0.1,
            )
            
            content = response.choices[0].message.content.strip()
            
            # Clean markdown
            if content.startswith('```json'):
                content = content[7:]
            elif content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            medication_data = json.loads(content)
            
            # Validate criticality
            valid_criticalities = ['low', 'medium', 'high', 'critical']
            if 'criticality' not in medication_data or medication_data['criticality'] not in valid_criticalities:
                medication_data['criticality'] = 'medium'
            
            return {
                'success': True,
                'data': medication_data
            }
            
        except json.JSONDecodeError as e:
            current_app.logger.error(f"JSON parsing error: {str(e)}")
            return {
                'success': False,
                'error': 'Could not parse medication package information',
                'details': str(e)
            }
        except Exception as e:
            current_app.logger.error(f"Medication image analysis error: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to analyze medication image',
                'details': str(e)
            }
    
    def analyze_medication_text(self, medication_info):
        """
        Analyze medication information from text and determine criticality
        
        Args:
            medication_info: dict with keys like medication_name, dosage, condition, etc.
        
        Returns:
            dict with criticality analysis
        """
        try:
            prompt = f"""Analyze this medication and provide criticality assessment:

Medication Name: {medication_info.get('medication_name', 'N/A')}
Generic Name: {medication_info.get('generic_name', 'N/A')}
Dosage: {medication_info.get('dosage', 'N/A')}
Frequency: {medication_info.get('frequency', 'N/A')}
Medical Condition: {medication_info.get('medical_condition', 'N/A')}

Provide criticality assessment (low/medium/high/critical) with reasoning.

Return ONLY valid JSON:
{{
    "criticality": "low|medium|high|critical",
    "explanation": "detailed explanation of why this criticality level",
    "adherence_notes": "important considerations for taking this medication",
    "risks": "risks of missing doses or stopping medication",
    "drug_class": "class of medication if identifiable"
}}"""

            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a medication safety expert. Assess medication criticality based on:
                        - Potential consequences of missed doses
                        - Treatment of life-threatening conditions
                        - Risk of withdrawal or discontinuation
                        - Whether medication replaces vital body function
                        
                        Be conservative and evidence-based."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=800,
                temperature=0.2,
            )
            
            content = response.choices[0].message.content.strip()
            
            # Clean markdown
            if content.startswith('```json'):
                content = content[7:]
            elif content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            analysis = json.loads(content)
            
            # Validate criticality
            valid_criticalities = ['low', 'medium', 'high', 'critical']
            if 'criticality' not in analysis or analysis['criticality'] not in valid_criticalities:
                analysis['criticality'] = 'medium'
            
            return {
                'success': True,
                'analysis': analysis
            }
            
        except json.JSONDecodeError as e:
            current_app.logger.error(f"JSON parsing error in text analysis: {str(e)}")
            return {
                'success': False,
                'error': 'Could not parse medication analysis',
                'details': str(e)
            }
        except Exception as e:
            current_app.logger.error(f"Text analysis error: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to analyze medication',
                'details': str(e)
            }
