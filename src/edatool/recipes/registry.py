"""Recipe registry for discovering and retrieving recipes."""

from __future__ import annotations

from edatool.recipes.base import RecipeBase

_REGISTRY: dict[str, RecipeBase] = {}


def register_recipe(recipe: RecipeBase) -> None:
    """Register a recipe instance in the global registry."""
    _REGISTRY[recipe.name] = recipe


def get_recipe(name: str) -> RecipeBase | None:
    """Look up a recipe by name. Returns None if not found."""
    _ensure_loaded()
    return _REGISTRY.get(name)


def list_recipes() -> list[RecipeBase]:
    """Return all registered recipes."""
    _ensure_loaded()
    return list(_REGISTRY.values())


def _ensure_loaded() -> None:
    """Lazy-load built-in recipes on first access."""
    if _REGISTRY:
        return
    from edatool.recipes.ab_test import ABTestRecipe

    register_recipe(ABTestRecipe())
