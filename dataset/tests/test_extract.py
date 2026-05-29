from __future__ import annotations

import zipfile

from dataset.data_download import (
    extract_downloaded_file_groups,
    extract_file,
    extract_files,
    multipart_extract_dir,
)


def test_extract_file_extracts_next_to_archive(tmp_path):
    archive_path = tmp_path / "example.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("nested/file.txt", "content")

    result = extract_file(archive_path)

    assert result.success
    assert (tmp_path / "example/nested/file.txt").read_text() == "content"


def test_extract_file_skips_existing_output_by_default(tmp_path):
    archive_path = tmp_path / "example.zip"
    output_dir = tmp_path / "example"
    output_dir.mkdir()
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("file.txt", "content")

    result = extract_file(archive_path)

    assert result.success
    assert result.skipped
    assert not (output_dir / "file.txt").exists()


def test_extract_file_rejects_unsafe_archive_paths(tmp_path):
    archive_path = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("../outside.txt", "bad")

    result = extract_file(archive_path)

    assert not result.success
    assert "Unsafe path" in result.error
    assert not (tmp_path / "outside.txt").exists()


def test_extract_files_filters_non_zip_manifest_paths(tmp_path):
    archive_path = tmp_path / "folder/example.zip"
    archive_path.parent.mkdir()
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("file.txt", "content")

    results = extract_files(["folder/example.zip", "folder/example.csv"], tmp_path)

    assert len(results) == 1
    assert results[0].success
    assert (tmp_path / "folder/example/file.txt").read_text() == "content"


def test_multipart_extract_dir_removes_part_suffix():
    assert multipart_extract_dir("parts/dataset-part-23.zip").as_posix() == "parts/dataset"


def test_extract_downloaded_file_groups_waits_for_complete_group(tmp_path):
    archive_a = tmp_path / "parts/dataset-part-00.zip"
    archive_b = tmp_path / "parts/dataset-part-01.zip"
    archive_a.parent.mkdir()
    for archive_path, file_name in [(archive_a, "a.txt"), (archive_b, "b.txt")]:
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.writestr(file_name, "content")

    results = extract_downloaded_file_groups(
        [["parts/dataset-part-00.zip", "parts/dataset-part-01.zip"]],
        tmp_path,
        successful_files={"parts/dataset-part-00.zip"},
    )

    assert results == []
    assert not (tmp_path / "parts/dataset/a.txt").exists()
    assert not (tmp_path / "parts/dataset/b.txt").exists()


def test_extract_downloaded_file_groups_extracts_complete_group(tmp_path):
    archive_a = tmp_path / "parts/dataset-part-00.zip"
    archive_b = tmp_path / "parts/dataset-part-01.zip"
    archive_a.parent.mkdir()
    for archive_path, file_name in [(archive_a, "a.txt"), (archive_b, "b.txt")]:
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.writestr(file_name, "content")

    results = extract_downloaded_file_groups(
        [["parts/dataset-part-00.zip", "parts/dataset-part-01.zip"]],
        tmp_path,
        successful_files={"parts/dataset-part-00.zip", "parts/dataset-part-01.zip"},
    )

    assert [result.success for result in results] == [True, True]
    assert (tmp_path / "parts/dataset/a.txt").read_text() == "content"
    assert (tmp_path / "parts/dataset/b.txt").read_text() == "content"
    assert (tmp_path / "parts/dataset/.geoplant_extract_complete").exists()


def test_extract_downloaded_file_groups_resumes_incomplete_existing_group(tmp_path):
    archive_a = tmp_path / "parts/dataset-part-00.zip"
    archive_b = tmp_path / "parts/dataset-part-01.zip"
    output_dir = tmp_path / "parts/dataset"
    archive_a.parent.mkdir()
    output_dir.mkdir()
    (output_dir / "a.txt").write_text("old")
    for archive_path, file_name in [(archive_a, "a.txt"), (archive_b, "b.txt")]:
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.writestr(file_name, "content")

    results = extract_downloaded_file_groups(
        [["parts/dataset-part-00.zip", "parts/dataset-part-01.zip"]],
        tmp_path,
        successful_files={"parts/dataset-part-00.zip", "parts/dataset-part-01.zip"},
    )

    assert [result.success for result in results] == [True, True]
    assert [result.skipped for result in results] == [False, False]
    assert (output_dir / "a.txt").read_text() == "content"
    assert (output_dir / "b.txt").read_text() == "content"
    assert (output_dir / ".geoplant_extract_complete").exists()


def test_extract_downloaded_file_groups_skips_existing_complete_group(tmp_path):
    archive_a = tmp_path / "parts/dataset-part-00.zip"
    archive_b = tmp_path / "parts/dataset-part-01.zip"
    output_dir = tmp_path / "parts/dataset"
    archive_a.parent.mkdir()
    output_dir.mkdir()
    (output_dir / ".geoplant_extract_complete").write_text("done\n")
    for archive_path, file_name in [(archive_a, "a.txt"), (archive_b, "b.txt")]:
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.writestr(file_name, "content")

    results = extract_downloaded_file_groups(
        [["parts/dataset-part-00.zip", "parts/dataset-part-01.zip"]],
        tmp_path,
        successful_files={"parts/dataset-part-00.zip", "parts/dataset-part-01.zip"},
    )

    assert [result.success for result in results] == [True, True]
    assert [result.skipped for result in results] == [True, True]
    assert not (output_dir / "a.txt").exists()
    assert not (output_dir / "b.txt").exists()
