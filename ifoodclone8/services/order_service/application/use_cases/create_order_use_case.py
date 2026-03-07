"""
Create Order Use Case
====================
Caso de uso para criação de novos pedidos.
"""

import sys
from pathlib import Path

# Adiciona o diretório do serviço ao path
service_path = Path(__file__).parent.parent.parent
if str(service_path) not in sys.path:
    sys.path.insert(0, str(service_path))

from domain.order_entities import Order
from domain.order_aggregates import OrderAggregate, OrderFactory
from domain.order_value_objects import OrderId, CustomerId, ProductId
from infrastructure.repositories import OrderRepository
from application.dtos import CreateOrderDTO


class CreateOrderUseCase:
    """Caso de uso para criar um novo pedido."""
    
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository
    
    def execute(self, dto: CreateOrderDTO) -> dict:
        """
        Executa a criação de um novo pedido.
        
        Args:
            dto: DTO com dados do pedido
            
        Returns:
            Dicionário com dados do pedido criado
        """
        # Cria o agregado de pedido
        aggregate = OrderFactory.create_order_aggregate(
            customer_id=dto.customer_id,
            items=dto.items
        )
        
        # Prepara os dados para salvamento
        order_data = {
            'customer_id': dto.customer_id,
            'items': [
                {
                    'product_id': item.get('product_id', ''),
                    'product_name': item.get('product_name', ''),
                    'quantity': item.get('quantity', 1),
                    'price': item.get('price', 0.0)
                }
                for item in dto.items
            ],
            'status': 'PENDING',
            'total': aggregate.calculate_total(),
            'notes': dto.notes,
            'delivery_address': dto.delivery_address
        }
        
        # Salva o pedido
        saved_order = self.order_repository.save(order_data)
        
        return saved_order


class GetOrderUseCase:
    """Caso de uso para buscar um pedido."""
    
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository
    
    def execute(self, order_id: int) -> dict:
        """
        Busca um pedido pelo ID.
        
        Args:
            order_id: ID do pedido
            
        Returns:
            Dicionário com dados do pedido ou None
        """
        return self.order_repository.get_by_id(order_id)


class ListOrdersUseCase:
    """Caso de uso para listar pedidos."""
    
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository
    
    def execute(self, skip: int = 0, limit: int = 100) -> list:
        """
        Lista pedidos com paginação.
        
        Args:
            skip: Número de registros a pular
            limit: Número máximo de registros a retornar
            
        Returns:
            Lista de pedidos
        """
        return self.order_repository.get_all(skip=skip, limit=limit)


class UpdateOrderStatusUseCase:
    """Caso de uso para atualizar status do pedido."""
    
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository
    
    def execute(self, order_id: int, new_status: str) -> dict:
        """
        Atualiza o status de um pedido.
        
        Args:
            order_id: ID do pedido
            new_status: Novo status
            
        Returns:
            Dicionário com dados do pedido atualizado
        """
        order_data = {'status': new_status}
        return self.order_repository.update(order_id, order_data)


class CancelOrderUseCase:
    """Caso de uso para cancelar um pedido."""
    
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository
    
    def execute(self, order_id: int) -> bool:
        """
        Cancela um pedido.
        
        Args:
            order_id: ID do pedido
            
        Returns:
            True se cancelado com sucesso, False caso contrário
        """
        # Primeiro busca o pedido para verificar se pode ser cancelado
        order = self.order_repository.get_by_id(order_id)
        if order and order.get('status') in ['PENDING', 'CONFIRMED']:
            self.order_repository.update(order_id, {'status': 'CANCELLED'})
            return True
        return False

