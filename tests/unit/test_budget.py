# tests/unit/test_budget.py

import pytest
from datetime import date
from src.models.budget import Budget

class TestBudgetModel:
    """Tests du modèle Budget"""
    
    def test_create_valid_budget(self):
        """Test: création d'un budget valide"""
        b = Budget(
            category_id=1,
            amount=300,
            period_start=date(2026, 1, 1),
            period_end=date(2026, 1, 31)
        )
        assert b.amount == 300
        assert b.category_id == 1
    
    def test_reject_negative_budget(self):
        """Test: rejet d'un budget négatif"""
        with pytest.raises(ValueError, match="Le montant du budget doit être positif"):
            Budget(
                category_id=1,
                amount=-100,
                period_start=date(2026, 1, 1),
                period_end=date(2026, 1, 31)
            )
    
    def test_reject_zero_budget(self):
        """Test: rejet d'un budget à zéro"""
        with pytest.raises(ValueError, match="Le montant du budget doit être positif"):
            Budget(
                category_id=1,
                amount=0,
                period_start=date(2026, 1, 1),
                period_end=date(2026, 1, 31)
            )
    
    def test_reject_invalid_period(self):
        """Test: rejet d'une période invalide (début après fin)"""
        with pytest.raises(ValueError, match="La date de début doit être antérieure"):
            Budget(
                category_id=1,
                amount=300,
                period_start=date(2026, 1, 31),
                period_end=date(2026, 1, 1)
            )
    
    def test_reject_same_dates(self):
        """Test: rejet si début et fin sont identiques"""
        with pytest.raises(ValueError, match="La date de début doit être antérieure"):
            Budget(
                category_id=1,
                amount=300,
                period_start=date(2026, 1, 15),
                period_end=date(2026, 1, 15)
            )
    
    def test_is_active_for_date(self):
        """Test: vérification si le budget est actif pour une date"""
        b = Budget(
            category_id=1,
            amount=300,
            period_start=date(2026, 1, 1),
            period_end=date(2026, 1, 31)
        )
        assert b.is_active_for_date(date(2026, 1, 15)) is True
        assert b.is_active_for_date(date(2026, 1, 1)) is True  # Limite incluse
        assert b.is_active_for_date(date(2026, 1, 31)) is True  # Limite incluse
        assert b.is_active_for_date(date(2026, 2, 1)) is False
        assert b.is_active_for_date(date(2025, 12, 31)) is False
    
    def test_to_dict(self):
        """Test: conversion en dictionnaire"""
        b = Budget(
            id=1,
            category_id=2,
            amount=500.0,
            period_start=date(2026, 1, 1),
            period_end=date(2026, 1, 31)
        )
        d = b.to_dict()
        assert d['id'] == 1
        assert d['category_id'] == 2
        assert d['amount'] == 500.0
        assert d['period_start'] == "2026-01-01"
        assert d['period_end'] == "2026-01-31"
