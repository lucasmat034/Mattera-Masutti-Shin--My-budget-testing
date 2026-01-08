# tests/unit/test_transaction.py

import pytest
from datetime import date
from src.models.transaction import Transaction

class TestTransactionModel:
    """Tests du modèle Transaction"""
    
    def test_create_valid_transaction(self):
        """Test: création d'une transaction valide"""
        t = Transaction(
            amount=25.50,
            description="Courses Leclerc",
            type="dépense",
            category_id=1,
            date=date(2026, 1, 6)
        )
        assert t.amount == 25.50
        assert t.description == "Courses Leclerc"
        assert t.type == "dépense"
    
    def test_reject_negative_amount(self):
        """Test: rejet d'un montant négatif"""
        with pytest.raises(ValueError, match="Le montant doit être positif"):
            Transaction(
                amount=-10,
                description="Test",
                type="dépense",
                category_id=1,
                date=date.today()
            )
    
    def test_reject_zero_amount(self):
        """Test: rejet d'un montant à zéro"""
        with pytest.raises(ValueError, match="Le montant doit être positif"):
            Transaction(
                amount=0,
                description="Test",
                type="dépense",
                category_id=1,
                date=date.today()
            )
    
    def test_reject_invalid_type(self):
        """Test: rejet d'un type invalide"""
        with pytest.raises(ValueError, match="Le type doit être"):
            Transaction(
                amount=10,
                description="Test",
                type="invalide",
                category_id=1,
                date=date.today()
            )
    
    def test_reject_empty_description(self):
        """Test: rejet d'une description vide"""
        with pytest.raises(ValueError, match="La description ne peut pas être vide"):
            Transaction(
                amount=10,
                description="",
                type="dépense",
                category_id=1,
                date=date.today()
            )
    
    def test_to_dict(self):
        """Test: conversion en dictionnaire"""
        t = Transaction(
            id=1,
            amount=50.0,
            description="Test",
            type="revenu",
            category_id=2,
            date=date(2026, 1, 10)
        )
        d = t.to_dict()
        assert d['id'] == 1
        assert d['amount'] == 50.0
        assert d['description'] == "Test"
        assert d['type'] == "revenu"
        assert d['category_id'] == 2
        assert d['date'] == "2026-01-10"
