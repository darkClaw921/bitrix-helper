from crmWork import BaseCrm
from fast_bitrix24 import BitrixAsync, Bitrix
from typing import Dict, Any, List

class BitrixCrm(BaseCrm):
    """Класс для работы с Bitrix24 CRM"""
    
    def __init__(self, webhook: str):
        super().__init__(webhook)
        self.bit = BitrixAsync(webhook, ssl=False)
        # self.bit = Bitrix(webhook)
        
    async def get_deal(self, dealID: int) -> Dict[str, Any]:
        """Получить сделку по ID"""
        deal = await self.bit.call('crm.deal.get', items={'ID': dealID})
        return deal['order0000000000']

    async def get_deals_by_filter(self, filter: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Получить сделки по фильтру"""
        deals = await self.bit.get_all('crm.deal.list', params=filter)
        return deals
    
    async def get_entity(self, entity_type: str, entity_id: int) -> Dict[str, Any]:
        """Получить сущность по ID"""
        return await self.bit.call(f'crm.entity.get', items={'ID': entity_id})
    
    async def get_entities_by_filter(self, entity_type: str, filter: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Получить сущности по фильтру"""
        return await self.bit.call(f'crm.entity.{entity_type}.list', items=filter)


    async def get_lead(self, leadID: int) -> Dict[str, Any]:
        """Получить лид по ID"""
        return await self.bit.call('crm.lead.get', items={'ID': leadID})
    
    async def get_leads_by_filter(self, filter: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Получить лиды по фильтру"""
        return await self.bit.call('crm.lead.list', items=filter)
    
    async def get_contact(self, contactID: int) -> Dict[str, Any]:
        """Получить контакт по ID"""
        return await self.bit.call('crm.contact.get', items={'ID': contactID})
    
    async def get_company(self, companyID: int) -> Dict[str, Any]:
        """Получить компанию по ID"""
        return await self.bit.call('crm.company.get', items={'ID': companyID})
    
    async def get_deal_fields(self) -> Dict[str, Any]:
        """Получить все поля сделки"""
        return await self.bit.call('crm.deal.fields')
    
    async def get_lead_fields(self) -> Dict[str, Any]:
        """Получить все поля лида"""
        return await self.bit.call('crm.lead.fields')
    
    async def get_contact_fields(self) -> Dict[str, Any]:
        """Получить все поля контакта"""
        return await self.bit.call('crm.contact.fields')
    
    async def get_company_fields(self) -> Dict[str, Any]:
        """Получить все поля компании"""
        return await self.bit.call('crm.company.fields')
    
    async def get_all_fields(self) -> Dict[str, Dict[str, Any]]:
        """Получить все поля всех сущностей"""
        return {
            'deal': await self.get_deal_fields(),
            'lead': await self.get_lead_fields(),
            'contact': await self.get_contact_fields(),
            'company': await self.get_company_fields()
        }
    
    async def get_all_fields_names(self) -> Dict[str, List[str]]:
        """Получить имена всех полей"""
        fields = await self.get_all_fields()
        return {
            entity: [field['title'] for field in fields[entity].values()]
            for entity in fields
        }
    
    async def get_all_fields_ids(self) -> Dict[str, List[str]]:
        """Получить ID всех полей"""
        fields = await self.get_all_fields()
        return {
            entity: list(fields[entity].keys())
            for entity in fields
        }
    
    async def update_deal(self, deal_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Обновить сделку"""
        return await self.bit.call('crm.deal.update', items={'ID': deal_id, 'fields': fields})
    
    async def update_lead(self, lead_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Обновить лид"""
        return await self.bit.call('crm.lead.update', items={'ID': lead_id, 'fields': fields})
    
    async def update_contact(self, contact_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Обновить контакт"""
        return await self.bit.call('crm.contact.update', items={'ID': contact_id, 'fields': fields})
    
    async def update_company(self, company_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Обновить компанию"""
        return await self.bit.call('crm.company.update', items={'ID': company_id, 'fields': fields})
    
    async def update_entity(self, entity_type: str, entity_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Обновить сущность"""
        return await self.bit.call(f'crm.{entity_type}.update', items={'ID': entity_id, 'fields': fields})
    
    