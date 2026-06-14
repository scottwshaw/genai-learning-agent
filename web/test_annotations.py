"""Tests for annotation persistence."""

from pathlib import Path

import pytest

from annotations import load_annotations, save_annotation


class TestAnnotationPersistence:
    """Loading and saving annotations for a brief."""

    def test_load_returns_empty_when_no_file(self, tmp_path):
        """Given a brief directory with no annotations.json,
        when load_annotations is called,
        then it returns an empty dict."""
        result = load_annotations(tmp_path)

        assert result == {}

    def test_save_creates_annotation(self, tmp_path):
        """Given no annotations exist,
        when save_annotation is called,
        then load_annotations returns the saved data."""
        save_annotation(tmp_path, "key-developments/0", {"interesting": True})

        result = load_annotations(tmp_path)

        assert result["key-developments/0"]["interesting"] is True

    def test_save_merges_with_existing(self, tmp_path):
        """Given an annotation already exists,
        when save_annotation is called for a different item,
        then both annotations are present."""
        save_annotation(tmp_path, "key-developments/0", {"interesting": True})
        save_annotation(tmp_path, "key-developments/1", {"interesting": False})

        result = load_annotations(tmp_path)

        assert result["key-developments/0"]["interesting"] is True
        assert result["key-developments/1"]["interesting"] is False

    def test_save_updates_existing_item(self, tmp_path):
        """Given an annotation exists for an item,
        when save_annotation is called again for the same item,
        then the annotation is updated."""
        save_annotation(tmp_path, "key-developments/0", {"interesting": True})
        save_annotation(tmp_path, "key-developments/0", {"interesting": False})

        result = load_annotations(tmp_path)

        assert result["key-developments/0"]["interesting"] is False
