from typing import Any

class Reporter:
    @staticmethod
    def SReport(report: dict[str, dict[str, Any]], *, leftcolumn: str = "", beautify: bool = False) -> str:
        """
        Convert a report dictionary into a Markdown-style table.

        The report is expected to look roughly like:

            {
                "extension.name": {
                    "type": "load",
                    "success": True,
                    "err": None
                }
            }

        Each key in the inner dictionaries becomes a column. Different entries
        may contain different fields; missing fields are left blank.

        Parameters:
            report (dict[str, dict[str, Any]]): A dict containing strings as keys and dicts as values.
            beautify (bool): Adds padding so the columns line up in monospace output.
            leftcolumn (str): Name of the column containing the keys from the outer dictionary.

        Returns:
            str: The formatted table based on the report dictionary.
        """

        # Discover every field used by every report entry.
        # dict.fromkeys() preserves the order in which fields were first seen
        # while removing duplicates.
        discoveredReporters = []

        for _, item in report.items():
            item: dict
            discoveredReporters.extend(item.keys())

        discoveredReporters = list(dict.fromkeys(discoveredReporters))

        col_widths = []

        if beautify:
            # Work out the required width for every column so the resulting
            # table is aligned when printed in a monospace terminal.
            first_col_width = max(len(str(k)) for k in report.keys())
            col_widths.append(first_col_width)

            for reporter in discoveredReporters:
                max_width = max(
                    len(str(item.get(reporter, "")))
                    for item in report.values()
                )

                # A column must also be wide enough for its header.
                max_width = max(max_width, len(reporter))
                col_widths.append(max_width)

        Table = []

        if beautify:
            # Padded Markdown-style header.
            header = (
                "| "
                + " | ".join(
                    str(r).ljust(w)
                    for r, w in zip(
                        [leftcolumn] + discoveredReporters,
                        col_widths
                    )
                )
                + " |"
            )
        else:
            # Compact table with no padding.
            header = (
                f"|{leftcolumn}|"
                + "|".join(discoveredReporters)
                + "|"
            )

        Table.append(header)

        if beautify:
            # Separator uses the same calculated widths as the header/data.
            sep = "|-" + "-|-".join("-" * w for w in col_widths) + "-|"
        else:
            # Compact separator: one separator section per column.
            sep = "|-" * (len(discoveredReporters) + 1) + "|"

        Table.append(sep)

        for key, item in report.items():
            item: dict

            if beautify:
                # Start with the outer dictionary key, then add each discovered
                # field in the same order as the header.
                entry = "| " + str(key).ljust(col_widths[0]) + " |"

                for i, reporter in enumerate(discoveredReporters):
                    val = str(
                        item.get(reporter, "")
                    ).ljust(col_widths[i + 1])

                    entry += " " + val + " |"

            else:
                # Compact output doesn't need any width calculations.
                entry = f"|{key}|"

                for reporter in discoveredReporters:
                    entry += str(item.get(reporter, "")) + "|"

            Table.append(entry)

        # The caller can print this directly or include it elsewhere.
        return "\n".join(Table)

if __name__ == "__main__":
    # Simple standalone example showing the expected report structure and
    # what the beautified output looks like.
    print(
        Reporter.SReport(
            {
                "reportpart1": {
                    "success": True
                },
                "reportpart2": {
                    "success": False,
                    "err": "f"
                },
                "reportpart3": {
                    "success": True,
                    "other": "some details"
                }
            },
            beautify=True
        )
    )