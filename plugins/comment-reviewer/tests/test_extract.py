from pathlib import Path

import extract_comments as ec
import paths


def spans(name):
    return ec.extract(paths.SAMPLES / name)["comments"]


def texts(name):
    return [c["text"] for c in spans(name)]


def test_go_line_and_block_spans():
    result = spans("sample.go")
    first = result[0]
    assert (first["start_line"], first["end_line"], first["kind"]) == (1, 1, "line")
    block = [c for c in result if c["kind"] == "block"]
    assert len(block) == 1
    assert (block[0]["start_line"], block[0]["end_line"]) == (4, 5)


def test_go_ignores_double_slash_inside_strings():
    """The positive count is load-bearing: every `assert not any(...)` below
    passes trivially on an empty list, which is exactly what happened when the
    samples lived in a directory the extractor skips."""
    found = texts("sample.go")
    assert len(found) == 3          # leading, block, trailing
    assert not any("example.com" in t for t in found)
    assert not any("back" in t for t in found)


def test_go_finds_the_trailing_comment():
    assert any("trailing" in t for t in texts("sample.go"))


def test_python_ignores_hash_inside_strings():
    found = texts("sample.py")
    assert len(found) == 4          # module docstring, line, fn docstring, trailing
    assert not any("not a comment" in t for t in found)
    assert not any("single" in t for t in found)


def test_python_captures_the_module_docstring_span():
    docstrings = [c for c in spans("sample.py") if "Module docstring" in c["text"]]
    assert len(docstrings) == 1
    assert (docstrings[0]["start_line"], docstrings[0]["end_line"]) == (1, 2)
    assert docstrings[0]["kind"] == "docstring"


def test_python_captures_the_function_docstring():
    docstrings = [c for c in spans("sample.py") if "Function docstring" in c["text"]]
    assert len(docstrings) == 1
    assert docstrings[0]["start_line"] == 12
    assert docstrings[0]["kind"] == "docstring"


def test_python_leaves_a_triple_quoted_data_string_alone():
    """A triple-quoted literal that is not in docstring position is data. Emitting
    it as a comment would invite the reviewer to rewrite a live string."""
    found = texts("sample.py")
    assert len(found) == 4
    assert not any("not a docstring" in t for t in found)
    assert not any("just data" in t for t in found)


def test_python_line_comment_after_the_docstring():
    leading = [c for c in spans("sample.py") if "leading comment" in c["text"]]
    assert len(leading) == 1
    assert leading[0]["start_line"] == 4 and leading[0]["kind"] == "line"


def test_shell_ignores_hash_inside_quotes():
    found = texts("sample.sh")
    assert len(found) == 2          # shebang, real comment
    assert not any("inside quotes" in t for t in found)


def test_sql_double_dash():
    assert len(texts("sample.sql")) == 2


def test_typescript_ignores_slashes_in_strings():
    found = texts("sample.ts")
    assert len(found) == 2          # line, block
    assert not any("inside" in t for t in found)


def test_yaml_finds_the_comment_after_an_apostrophe():
    """An apostrophe in prose used to open a string that swallowed the rest of
    the file."""
    assert any("trailing" in t for t in texts("sample.yaml"))


def test_html_finds_the_comment_after_an_apostrophe():
    assert any("trailing" in t for t in texts("sample.html"))


def test_rust_nested_block_span_covers_the_whole_comment():
    block = [c for c in spans("sample.rs") if c["kind"] == "block"][0]
    assert block["text"].endswith("*/")
    assert block["text"].count("/*") == 2


def test_lua_long_bracket_comment_is_one_block():
    assert any(c["kind"] == "block" for c in spans("sample.lua"))


def test_nix_finds_its_comments():
    assert len(texts("sample.nix")) >= 2


def test_multi_language_files_are_skipped_not_half_scanned(tmp_path):
    """A .vue file needs per-block token selection; scanning it with the HTML
    table would silently miss every comment in its script block."""
    target = tmp_path / "c.vue"
    target.write_text("<template><!-- t --></template>\n<script>// s\n</script>\n")
    assert ec.extract(target)["skipped"] == "multi-language-unsupported"


def test_detect_language_by_extension():
    assert ec.detect_language(Path("a.go")) == "go"
    assert ec.detect_language(Path("a.tsx")) == "typescript"


def test_detect_language_by_shebang(tmp_path):
    script = tmp_path / "noext"
    script.write_text("#!/usr/bin/env python3\n# hi\n")
    assert ec.detect_language(script) == "python"


def test_unknown_extension_is_skipped_not_guessed(tmp_path):
    odd = tmp_path / "a.qqq"
    odd.write_text("// hi\n")
    assert ec.extract(odd)["skipped"] == "unknown-language"


def test_binary_file_is_skipped(tmp_path):
    blob = tmp_path / "a.go"
    blob.write_bytes(b"package main\x00\x00binary")
    assert ec.extract(blob)["skipped"] == "binary"


def test_oversized_file_is_skipped(tmp_path):
    big = tmp_path / "big.go"
    big.write_text("// c\n" + "x = 1\n" * 200_000)
    assert ec.extract(big)["skipped"] == "too-large"


def test_missing_file_is_skipped(tmp_path):
    assert ec.extract(tmp_path / "gone.go")["skipped"] == "unreadable"


def test_markdown_is_out_of_scope(tmp_path):
    doc = tmp_path / "a.md"
    doc.write_text("<!-- hi -->\n")
    assert ec.extract(doc)["skipped"] == "markdown-out-of-scope"


def test_main_reads_paths_from_stdin(tmp_path, capsys, monkeypatch):
    import io, json, sys
    target = paths.SAMPLES / "sample.go"
    monkeypatch.setattr(sys, "stdin", io.StringIO(f"{target}\n"))
    ec.main()
    payload = json.loads(capsys.readouterr().out)
    assert payload["files"][0]["lang"] == "go"


# --- Fix round: three Critical findings, all in EXTENSIONS/LANGS mappings. ---
# Each test is paired -- a data literal must NOT be emitted AND a real comment
# in the same file MUST still be found -- so none of these can pass vacuously
# by the extractor simply returning an empty list.


def test_toml_triple_quoted_string_is_not_scanned_for_comments(tmp_path):
    """FINDING 1: `.toml` used to map to the `shell` Lang, which has no
    multi-line string form, so a `#` inside a TOML triple-quoted string was
    emitted as a real line comment -- a data literal offered up for editing."""
    doc = tmp_path / "sample.toml"
    doc.write_text(
        "# real comment\n"
        'text = """\n'
        "# looks like a comment but is DATA inside a TOML string\n"
        '"""\n'
    )
    record = ec.extract(doc)
    assert record["lang"] == "toml"
    found = [c["text"] for c in record["comments"]]
    assert any("real comment" in t for t in found)
    assert not any("looks like a comment" in t for t in found)


def test_kotlin_raw_string_is_not_scanned_for_comments(tmp_path):
    """FINDING 2: `.kt` used to map to the `c` Lang, which has no
    triple-quoted form, so a `//` inside a Kotlin raw string was emitted as a
    real line comment."""
    doc = tmp_path / "sample.kt"
    doc.write_text(
        "// real comment\n"
        'val s = """\n'
        "// this is DATA inside a Kotlin raw string\n"
        '"""\n'
    )
    record = ec.extract(doc)
    assert record["lang"] == "kotlin"
    found = [c["text"] for c in record["comments"]]
    assert any("real comment" in t for t in found)
    assert not any("DATA inside a Kotlin" in t for t in found)


def test_kotlin_nested_block_comment_covers_the_whole_comment(tmp_path):
    """Kotlin block comments nest by specification, like Rust's -- the `c`
    Lang Kotlin used to borrow does not nest, so the first `*/` would end the
    comment early and leave a dangling ` still outer */` behind as code."""
    doc = tmp_path / "nested.kt"
    doc.write_text("/* outer /* inner */ still outer */\n// trailing\n")
    record = ec.extract(doc)
    assert record["lang"] == "kotlin"
    spans_ = record["comments"]
    block = [c for c in spans_ if c["kind"] == "block"][0]
    assert block["text"].endswith("*/")
    assert block["text"].count("/*") == 2
    assert any("trailing" in c["text"] for c in spans_)


def test_java_text_block_is_not_scanned_for_comments(tmp_path):
    """FINDING 2 (Java half): `.java` also used to map to the `c` Lang, so a
    `//` inside a Java text block was emitted as a real line comment."""
    doc = tmp_path / "sample.java"
    doc.write_text(
        "// real comment\n"
        'String s = """\n'
        "// this is DATA inside a Java text block\n"
        '""";\n'
    )
    record = ec.extract(doc)
    assert record["lang"] == "java"
    found = [c["text"] for c in record["comments"]]
    assert any("real comment" in t for t in found)
    assert not any("DATA inside a Java" in t for t in found)


def test_shell_heredoc_body_is_not_scanned_for_comments(tmp_path):
    """FINDING 3: a heredoc body is literal data passed to a command, not
    shell syntax, so a `#` inside it was emitted as a real line comment."""
    doc = tmp_path / "heredoc.sh"
    doc.write_text(
        "# real comment\n"
        "cat <<EOF\n"
        "this has a # inside heredoc\n"
        "EOF\n"
    )
    record = ec.extract(doc)
    found = [c["text"] for c in record["comments"]]
    assert any("real comment" in t for t in found)
    assert not any("inside heredoc" in t for t in found)


def test_shell_heredoc_with_dash_and_quoted_delimiter(tmp_path):
    """`<<-` strips leading tabs from the delimiter line, and a quoted
    delimiter (`<<'EOF'`) suppresses expansion inside the body -- neither
    changes that the body is data, not shell syntax."""
    doc = tmp_path / "heredoc2.sh"
    doc.write_text(
        "# real comment\n"
        "cat <<-'EOF'\n"
        "\tthis has a # inside heredoc too\n"
        "\tEOF\n"
    )
    record = ec.extract(doc)
    found = [c["text"] for c in record["comments"]]
    assert any("real comment" in t for t in found)
    assert not any("inside heredoc too" in t for t in found)


def test_shell_arithmetic_left_shift_is_not_a_heredoc_opener(tmp_path):
    """C1: `$((1 << SHIFT))` contains a `<<` that reads exactly like a heredoc
    opener to a scanner that only looks at the token in isolation. Mirrors
    test_match.py's `# F8` arithmetic case: without the `_ARITH_SPAN` guard,
    `SHIFT` is read as the heredoc delimiter and everything up to the next
    line that happens to read exactly `SHIFT` -- including a real comment --
    is swallowed as the heredoc body, while `extract()` still reports
    `"skipped": None` as if the file were fully, cleanly scanned."""
    doc = tmp_path / "arith.sh"
    doc.write_text(
        "mask=$((1 << SHIFT))\n"
        "# a real comment that must not vanish\n"
    )
    record = ec.extract(doc)
    assert record["skipped"] is None
    found = [c["text"] for c in record["comments"]]
    assert any("a real comment that must not vanish" in t for t in found)


def test_shell_multiline_arithmetic_shift_across_lines_is_not_a_heredoc_opener(tmp_path):
    """C1 re-review (Critical, round 2): the first fix's `_ARITH_SPAN` check
    was scoped to a single line, but `_HEREDOC_START`'s own `\\s*` matches a
    newline -- `$((` opened on one line, `<<` and its operand on the next,
    is normal bash formatting and the single-line check never sees the
    closing `))` at all, reproducing the original swallow-to-EOF bug."""
    doc = tmp_path / "arith_multiline.sh"
    doc.write_text(
        "mask=$((1 <<\n"
        "  SHIFT))\n"
        "# real comment after\n"
    )
    record = ec.extract(doc)
    assert record["skipped"] is None
    found = [c["text"] for c in record["comments"]]
    assert any("real comment after" in t for t in found)


def test_shell_multiline_arithmetic_block_is_not_a_heredoc_opener(tmp_path):
    """Second multi-line shape from the same finding: the whole `$((...))`
    expression on its own lines, with `<<` in the middle."""
    doc = tmp_path / "arith_block.sh"
    doc.write_text(
        "result=$((\n"
        "    value << SHIFT_AMOUNT\n"
        "))\n"
        "# a note about the result\n"
    )
    record = ec.extract(doc)
    assert record["skipped"] is None
    found = [c["text"] for c in record["comments"]]
    assert any("a note about the result" in t for t in found)


def test_shell_heredoc_after_unrelated_arithmetic_is_still_suppressed(tmp_path):
    """Regression guard for the fix to the fix: a naive DOTALL/lazy regex over
    the whole file would pair the FIRST `$((` with the NEXT `))` anywhere
    after it -- including one belonging to a second, unrelated arithmetic
    expression -- and would then wrongly treat everything up to there,
    including a real heredoc's `<<`, as inside an arithmetic span. A
    legitimate heredoc appearing after an unrelated `$(( ))` must still have
    its body suppressed as data, not scanned for comments."""
    doc = tmp_path / "heredoc_after_arith.sh"
    doc.write_text(
        "# real comment before\n"
        "mask=$((1 << SHIFT))\n"
        "cat <<EOF\n"
        "this has a # inside heredoc\n"
        "EOF\n"
        "# real comment after\n"
    )
    record = ec.extract(doc)
    assert record["skipped"] is None
    found = [c["text"] for c in record["comments"]]
    assert any("real comment before" in t for t in found)
    assert any("real comment after" in t for t in found)
    assert not any("inside heredoc" in t for t in found)


def test_js_extension_reports_javascript_not_typescript(tmp_path):
    """I5: `.js`/`.jsx` used to map onto the `typescript` Lang entry, so
    `extract()` reported `lang: "typescript"` for a plain JS file. That erases
    the JSDoc `@param` carve-out in comment-classes.md, which is keyed off
    the file being untyped: every downstream signal read "typed language,
    condensable" for a codebase whose JSDoc tags are its only type info."""
    doc = tmp_path / "a.js"
    doc.write_text("// hi\n")
    assert ec.extract(doc)["lang"] == "javascript"

    jsx = tmp_path / "a.jsx"
    jsx.write_text("// hi\n")
    assert ec.extract(jsx)["lang"] == "javascript"


def test_jsdoc_negative_fixture_reports_javascript_and_keeps_the_param_block(tmp_path):
    """The spec's verification table names tests/samples/negative/jsdoc.js
    explicitly: a JSDoc @param block in a .js file must be reported under the
    honest `javascript` label, not `typescript`, so the agent's never-touch
    carve-out for JSDoc in untyped files actually applies."""
    record = ec.extract(paths.NEGATIVE_SAMPLES / "jsdoc.js")
    assert record["lang"] == "javascript"
    assert any("@param" in c["text"] for c in record["comments"])


def test_python_triple_quoted_string_inside_function_body_is_not_a_docstring(tmp_path):
    """Regression guard: a triple-quoted literal that is not the first
    statement of a function -- here it follows an assignment -- is data, not
    a docstring, even though it sits inside a function body."""
    doc = tmp_path / "inline.py"
    doc.write_text(
        "def f():\n"
        "    x = 1\n"
        '    y = """not a docstring because an assignment precedes it\n'
        '    still just data"""\n'
        "    return y  # trailing\n"
    )
    record = ec.extract(doc)
    found = record["comments"]
    assert not any("not a docstring" in c["text"] for c in found)
    assert not any(c["kind"] == "docstring" for c in found)
    assert any("trailing" in c["text"] for c in found)
