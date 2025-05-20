#!/usr/bin/env python3
# Copyright 2025 ETH Zurich and University of Bologna.
# Licensed under the Apache License, Version 2.0, see LICENSE for details.
# SPDX-License-Identifier: Apache-2.0
#
# Author: Michael Rogenmoser <michaero@iis.ee.ethz.ch>

import os
from itertools import product
from peakrdl.plugins.exporter import ExporterSubcommandPlugin
from systemrdl.node import AddrmapNode, RegNode, MemNode, RegfileNode
from mako.template import Template

class HeaderGeneratorDescriptor(ExporterSubcommandPlugin):
    short_desc = "Generate C header with block base addresses and register offsets via Mako"
    long_desc = (
        "Walk the RDL tree and render a C header file from a Mako template, "
        "indicating base addresses for each addrmap block and offsets for each register."
    )

    def add_exporter_arguments(self, arg_group):
        arg_group.add_argument(
            "--template", default=None,
            help="Path to the Mako template file (defaults to templates in plugin dir)"
        )
        arg_group.add_argument(
            "--base_name", default=None,
            help="Custom prefix for the header (defaults to top-level map name)"
        )
        arg_group.add_argument(
            "--format", default="c",
            choices=["c", "svh", "svpkg"]
        )
        arg_group.add_argument(
            "--license_str", default=None,
            help="License string to include in the header file"
        )

    def do_export(self, top_node: AddrmapNode, options):
        output_path = options.output
        top_name = (options.base_name or top_node.inst_name)

        license_str = None
        if options.license_str:
            # Convert literal \n to actual newlines
            license_str = options.license_str.replace('\\n', '\n')

        # Load template
        if options.template:
            template_path = options.template
        else:
            if options.format == "c":
                template_path = os.path.join(os.path.dirname(__file__), "templates/c_header.tpl")
            elif options.format == "svh":
                template_path = os.path.join(os.path.dirname(__file__), "templates/svh.tpl")
            elif options.format == "svpkg":
                template_path = os.path.join(os.path.dirname(__file__), "templates/svpkg.tpl")
            else:
                # Default to C header template (shouldn't happen due to choices constraint)
                template_path = os.path.join(os.path.dirname(__file__), "templates/c_header.tpl")
        with open(template_path, "r") as tf:
            tmpl = Template(tf.read())

        # Get list for template
        # List consists of blocks that have a list of entries with name (addr, offset, size, or other) and a number
        blocks = get_regs(top_node)

        # for block in blocks:
        #     print(block)

        # Render and write
        rendered = tmpl.render(top_name=top_name, blocks=blocks, license_str=license_str)
        with open(output_path, "w") as f:
            f.write(rendered)


def get_regs(node: AddrmapNode, prefix: str = ""):
    """Recursively get all registers in the addrmap tree."""
    start_basename = prefix + node.inst_name.upper()
    nodes = []
    block = []
    subblock = []
    if node.is_array:
        nodes = node.unrolled()
    else:
        nodes = [node]

    for subnode in nodes:
        basename = start_basename
        if node.is_array:
            for idx in subnode.current_idx:
                basename += "_" + str(idx)
        if isinstance(subnode, RegNode):
            subblock.extend([{"name": basename + "_REG_ADDR  ", "num": subnode.absolute_address},
                             {"name": basename + "_REG_OFFSET", "num": subnode.address_offset}])
            block = [subblock]
        elif isinstance(subnode, AddrmapNode) or isinstance(node, RegfileNode):
            block.append([])
            block.append([{ "name": basename + "_BASE_ADDR", "num": subnode.absolute_address },
                          { "name": basename + "_SIZE     ", "num": subnode.total_size }])

            for child in subnode.children():
                block.extend(get_regs(child, basename + "_"))

        elif isinstance(subnode, MemNode):
            block.append([])
            block.append([{"name": basename + "_BASE_ADDR", "num": subnode.absolute_address},
                          {"name": basename + "_SIZE     ", "num": subnode.total_size}])
        else:
            print(f"Unknown node type: {type(node)}")

    return block
