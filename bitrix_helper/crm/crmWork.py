from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

class BaseCrm(ABC):
    """Базовый абстрактный класс для работы с CRM системами"""
    
    def __init__(self, webhook: str):
        self.webhook = webhook
    
    @abstractmethod
    def get_deal(self, deal_id: str) -> Dict[str, Any]:
        """Получить сделку по ID"""
        pass
    
    @abstractmethod
    def get_lead(self, lead_id: str) -> Dict[str, Any]:
        """Получить лид по ID"""
        pass

    @abstractmethod
    def get_contact(self, contact_id: str) -> Dict[str, Any]:
        """Получить контакт по ID"""
        pass

    @abstractmethod
    def get_company(self, company_id: str) -> Dict[str, Any]:
        """Получить компанию по ID"""
        pass

    @abstractmethod
    def get_deal_fields(self) -> Dict[str, Any]:
        """Получить все поля сделки"""
        pass

    @abstractmethod
    def get_lead_fields(self) -> Dict[str, Any]:
        """Получить все поля лида"""
        pass

    @abstractmethod
    def get_contact_fields(self) -> Dict[str, Any]:
        """Получить все поля контакта"""
        pass

    @abstractmethod
    def get_company_fields(self) -> Dict[str, Any]:
        """Получить все поля компании"""
        pass

    @abstractmethod
    def get_all_fields(self) -> Dict[str, Dict[str, Any]]:
        """Получить все поля всех сущностей"""
        pass

    @abstractmethod
    def get_all_fields_names(self) -> Dict[str, List[str]]:
        """Получить имена всех полей"""
        pass

    @abstractmethod
    def get_all_fields_ids(self) -> Dict[str, List[str]]:
        """Получить ID всех полей"""
        pass
