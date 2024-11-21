from typing import Optional, Dict, Any
from .crmWork import BaseCrm
from .workBitrix import BitrixCrm
# from .workAmo import AmoCrm  # Будущие CRM системы
# from .workZoho import ZohoCrm

class CrmHandler:
    """Класс для обработки запросов к различным CRM системам"""
    
    def __init__(self):
        self.crm_types = {
            'bitrix24': BitrixCrm,
            # 'amocrm': AmoCrm,
            # 'zohocrm': ZohoCrm
        }
        
    def get_crm_instance(self, crm_type: str, webhook: str) -> Optional[BaseCrm]:
        """
        Создает экземпляр нужного CRM класса
        
        Args:
            crm_type: Тип CRM системы
            webhook: Webhook для подключения к CRM
            
        Returns:
            Экземпляр соответствующего CRM класса или None
        """
        crm_class = self.crm_types.get(crm_type.lower())
        if crm_class:
            return crm_class(webhook)
        return None

    async def get_entity_info(self, 
                            crm_type: str,
                            webhook: str,
                            entity_type: str,
                            entity_id: str) -> Dict[str, Any]:
        """
        Получает информацию о сущности из CRM
        
        Args:
            crm_type: Тип CRM системы
            webhook: Webhook для подключения
            entity_type: Тип сущности (deal, lead, contact, company)
            entity_id: ID сущности
            
        Returns:
            Словарь с информацией о сущности
        """
        crm = self.get_crm_instance(crm_type, webhook)
        if not crm:
            return {'error': 'Неподдерживаемый тип CRM'}
            
        entity_methods = {
            'deal': crm.get_deal,
            'lead': crm.get_lead,
            'contact': crm.get_contact,
            'company': crm.get_company
        }
        
        method = entity_methods.get(entity_type.lower())
        if not method:
            return {'error': 'Неподдерживаемый тип сущности'}
            
        try:
            return method(entity_id)
        except Exception as e:
            return {'error': str(e)}

    async def get_fields_info(self,
                            crm_type: str,
                            webhook: str,
                            entity_type: str = None) -> Dict[str, Any]:
        """
        Получает информацию о полях сущности или всех полях
        
        Args:
            crm_type: Тип CRM системы
            webhook: Webhook для подключения
            entity_type: Тип сущности (опционально)
            
        Returns:
            Словарь с информацией о полях
        """
        crm = self.get_crm_instance(crm_type, webhook)
        if not crm:
            return {'error': 'Неподдерживаемый тип CRM'}
            
        if entity_type:
            field_methods = {
                'deal': crm.get_deal_fields,
                'lead': crm.get_lead_fields,
                'contact': crm.get_contact_fields,
                'company': crm.get_company_fields
            }
            method = field_methods.get(entity_type.lower())
            if not method:
                return {'error': 'Неподдерживаемый тип сущности'}
            return method()
        
        return crm.get_all_fields() 