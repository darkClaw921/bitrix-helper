from .crmWork import BaseCrm
from fast_bitrix24 import Bitrix
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

class BitrixCrm(BaseCrm):
    """Класс для работы с Bitrix24 CRM"""
    
    def __init__(self, webhook: str):
        super().__init__(webhook)
        self.bit = Bitrix(webhook)
        
    def get_deal(self, deal_id: str) -> Dict[str, Any]:
        """Получить сделку по ID"""
        return self.bit.call('crm.deal.get', items={'id': deal_id})
    
    def get_lead(self, lead_id: str) -> Dict[str, Any]:
        """Получить лид по ID"""
        return self.bit.call('crm.lead.get', params={'id': lead_id})
    
    def get_contact(self, contact_id: str) -> Dict[str, Any]:
        """Получить контакт по ID"""
        return self.bit.call('crm.contact.get', params={'id': contact_id})
    
    def get_company(self, company_id: str) -> Dict[str, Any]:
        """Получить компанию по ID"""
        return self.bit.call('crm.company.get', params={'id': company_id})
    
    def get_deal_fields(self) -> Dict[str, Any]:
        """Получить все поля сделки"""
        return self.bit.call('crm.deal.fields')
    
    def get_lead_fields(self) -> Dict[str, Any]:
        """Получить все поля лида"""
        return self.bit.call('crm.lead.fields')
    
    def get_contact_fields(self) -> Dict[str, Any]:
        """Получить все поля контакта"""
        return self.bit.call('crm.contact.fields')
    
    def get_company_fields(self) -> Dict[str, Any]:
        """Получить все поля компании"""
        return self.bit.call('crm.company.fields')
    
    def get_all_fields(self) -> Dict[str, Dict[str, Any]]:
        """Получить все поля всех сущностей"""
        return {
            'deal': self.get_deal_fields(),
            'lead': self.get_lead_fields(),
            'contact': self.get_contact_fields(),
            'company': self.get_company_fields()
        }
    
    def get_all_fields_names(self) -> Dict[str, List[str]]:
        """Получить имена всех полей"""
        fields = self.get_all_fields()
        return {
            entity: [field['title'] for field in fields[entity].values()]
            for entity in fields
        }
    
    def get_all_fields_ids(self) -> Dict[str, List[str]]:
        """Получить ID всех полей"""
        fields = self.get_all_fields()
        return {
            entity: list(fields[entity].keys())
            for entity in fields
        }
    