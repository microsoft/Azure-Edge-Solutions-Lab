# SPDX-FileCopyrightText: Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

import sys
import onnx
import numpy as np
import onnx_graphsurgeon as gs

# Load the original graph
graph = gs.import_onnx(onnx.load(sys.argv[1]))

# Find the softmax node
for node in graph.nodes:
    if node.op == "Softmax":
        # Create a [1, -1, 1, 1] Reshape node, connect it to the softmax's output, and set the graph output to this node
        shape = gs.Constant(name="output_shape", values=np.asarray([1, -1, 1, 1], dtype=np.int64))
        reshape = graph.layer(op="Reshape", name="reshaper", inputs=[node.outputs[0], shape], outputs=["reshaper_output"])
        graph.outputs = reshape

# Make sure the output is set to fp32
graph.outputs[0].dtype = np.float32

# Cleanup (remove leftover unconnected nodes) and save the new graph
graph.cleanup().toposort()
model = gs.export_onnx(graph)
onnx.save(model, sys.argv[2])

