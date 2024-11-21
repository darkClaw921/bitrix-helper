from typing import Optional, Dict, Any
from crmWork import BaseCrm
from workBitrix import BitrixCrm
# from .workAmo import AmoCrm  # Будущие CRM системы
# from .workZoho import ZohoCrm
from typing import Optional, Dict, Any, List
class CrmHandler:
    """Класс для обработки запросов к различным CRM системам"""
    
    def __init__(self, crm_type: str, webhook: str):
        """
        Инициализация обработчика CRM
        
        Args:
            crm_type: Тип CRM системы
            webhook: Webhook для подключения к CRM
        """
        self.crm_types = {
            'bitrix24': BitrixCrm,

            # 'amocrm': AmoCrm,
            # 'zohocrm': ZohoCrm
        }
        
        self.crm = self._init_crm(crm_type, webhook)
        
    def _init_crm(self, crm_type: str, webhook: str) -> Optional[BaseCrm]:
        """
        Инициализирует экземпляр CRM системы
        
        Args:
            crm_type: Тип CRM системы
            webhook: Webhook для подключения
            
        Returns:
            Экземпляр CRM класса или None
        """
        crm_class = self.crm_types.get(crm_type.lower())
        if crm_class:
            return crm_class(webhook)
        return None

    async def get_entity_info(self, 
                            entity_type: str,
                            entity_id: str) -> Dict[str, Any]:
        """
        Получает информацию о сущности из CRM
        
        Args:
            entity_type: Тип сущности (deal, lead, contact, company)
            entity_id: ID сущности
            
        Returns:
            Словарь с информацией о сущности
        """
        if not self.crm:
            return {'error': 'CRM не инициализирована'}
            
        entity_methods = {
            'deal': self.crm.get_deal,
            'lead': self.crm.get_lead,
            'contact': self.crm.get_contact,
            'company': self.crm.get_company
        }
        
        method = entity_methods.get(entity_type.lower())
        if not method:
            return {'error': 'Неподдерживаемый тип сущности'}
            
        try:
            return method(entity_id)
        except Exception as e:
            return {'error': str(e)}

    async def get_fields_info(self,
                            entity_type: str = None) -> Dict[str, Any]:
        """
        Получает информацию о полях сущности или всех полях
        
        Args:
            entity_type: Тип сущности (опционально)
            
        Returns:
            Словарь с информацией о полях
        """
        if not self.crm:
            return {'error': 'CRM не инициализирована'}
            
        if entity_type:
            field_methods = {
                'deal': self.crm.get_deal_fields,
                'lead': self.crm.get_lead_fields,
                'contact': self.crm.get_contact_fields,
                'company': self.crm.get_company_fields
            }
            method = field_methods.get(entity_type.lower())
            if not method:
                return {'error': 'Неподдерживаемый тип сущности'}
            return method()
        
        return self.crm.get_all_fields() 
    
    async def get_deals_by_filter(self, filter: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Получить сделки по фильтру"""
        return await self.crm.get_deals_by_filter(filter)
    
    async def get_leads_by_filter(self, filter: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Получить лиды по фильтру"""
        return await self.crm.get_leads_by_filter(filter)
    
    async def get_deal(self, dealID: int) -> Dict[str, Any]:
        """Получить сделку по ID"""
        return await self.crm.get_entity('deal', dealID)
    
    async def update_deal(self, dealID: int, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Обновить сделку"""
        return await self.crm.update_deal(dealID, fields)
    
    