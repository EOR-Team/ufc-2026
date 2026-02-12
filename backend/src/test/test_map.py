# test/test_map.py
# 地图相关功能测试
#

import json
from pydantic import ValidationError
from src.map import tools, typedef
from src import logger


# ============================================================================
# Test Data
# ============================================================================

# Valid test map data
VALID_MAP_JSON = """{
    "nodes": [
        {"id": "A", "x": 0, "y": 0, "type": "main", "name": "Node A", "description": "First node"},
        {"id": "B", "x": 1, "y": 0, "type": "nav"},
        {"id": "C", "x": 2, "y": 0, "type": "main", "name": "Node C"},
        {"id": "D", "x": 1, "y": 1, "type": "nav"},
        {"id": "E", "x": 2, "y": 1, "type": "main", "name": "Node E"}
    ],
    "edges": [
        {"u": "A", "v": "B"},
        {"u": "B", "v": "C"},
        {"u": "B", "v": "D"},
        {"u": "D", "v": "E"}
    ]
}"""

SIMPLE_MAP_JSON = """{
    "nodes": [
        {"id": "X", "x": 0, "y": 0, "type": "main"},
        {"id": "Y", "x": 3, "y": 4, "type": "main"}
    ],
    "edges": [
        {"u": "X", "v": "Y"}
    ]
}"""

DISCONNECTED_MAP_JSON = """{
    "nodes": [
        {"id": "A", "x": 0, "y": 0, "type": "main"},
        {"id": "B", "x": 1, "y": 0, "type": "main"},
        {"id": "C", "x": 2, "y": 0, "type": "main"}
    ],
    "edges": [
        {"u": "A", "v": "B"}
    ]
}"""


# ============================================================================
# Type Validation Tests
# ============================================================================

def test_node_type_validation():
    """Test Node type validation"""
    logger.info("=" * 60)
    logger.info("Testing Node Type Validation")
    logger.info("=" * 60)
    
    # Valid node
    try:
        node = typedef.Node(id="test1", x=1.5, y=2.5, type="main", name="Test Node", description=None)
        logger.info(f"✓ Valid node created: {node.id}")
    except ValidationError as e:
        logger.error(f"✗ Valid node creation failed: {e}")
    
    # Valid node with minimal fields
    try:
        node = typedef.Node(id="test2", x=0, y=0, type="nav", name=None, description=None)
        logger.info(f"✓ Minimal valid node created: {node.id}")
    except ValidationError as e:
        logger.error(f"✗ Minimal node creation failed: {e}")
    
    # Invalid type
    try:
        node = typedef.Node(id="test3", x=0, y=0, type="invalid", name=None, description=None)
        logger.error("✗ Should have failed: invalid type accepted")
    except ValidationError:
        logger.info("✓ Invalid type correctly rejected")
    
    # Missing required fields
    try:
        node = typedef.Node(id="test4", x=None, y=None, type=None, name=None, description=None)
        logger.error("✗ Should have failed: missing required fields")
    except ValidationError:
        logger.info("✓ Missing required fields correctly rejected")
    
    # Invalid coordinate types
    try:
        node = typedef.Node(id="test5", x="invalid", y=0, type="main", name=None, description=None)
        logger.error("✗ Should have failed: invalid coordinate type")
    except ValidationError:
        logger.info("✓ Invalid coordinate type correctly rejected")
    
    # Name too long (max 50 characters)
    try:
        long_name = "a" * 51
        node = typedef.Node(id="test6", x=0, y=0, type="main", name=long_name, description=None)
        logger.error("✗ Should have failed: name too long")
    except ValidationError:
        logger.info("✓ Name length validation works correctly")
    
    # Description too long (max 200 characters)
    try:
        long_desc = "a" * 201
        node = typedef.Node(id="test7", x=0, y=0, type="main", name=None, description=long_desc)
        logger.error("✗ Should have failed: description too long")
    except ValidationError:
        logger.info("✓ Description length validation works correctly")
    
    logger.info("")


def test_edge_type_validation():
    """Test Edge type validation"""
    logger.info("=" * 60)
    logger.info("Testing Edge Type Validation")
    logger.info("=" * 60)
    
    # Valid edge with alias 'u' and 'v'
    try:
        edge = typedef.Edge(u="A", v="B", cost=10, name="Edge AB")
        logger.info(f"✓ Valid edge created: {edge.u_node} -> {edge.v_node}")
    except ValidationError as e:
        logger.error(f"✗ Valid edge creation failed: {e}")
    
    # Valid edge with minimal fields
    try:
        edge = typedef.Edge(u="X", v="Y", cost=None, name=None)
        logger.info(f"✓ Minimal valid edge created: {edge.u_node} -> {edge.v_node}")
    except ValidationError as e:
        logger.error(f"✗ Minimal edge creation failed: {e}")
    
    # Using field names instead of aliases
    # Skipped: Edge does not accept u_node/v_node as parameters, only u/v
    
    # Missing required fields
    try:
        edge = typedef.Edge(u="A", v=None, cost=None, name=None)
        logger.error("✗ Should have failed: missing required field")
    except ValidationError:
        logger.info("✓ Missing required field correctly rejected")
    
    # Invalid cost type
    try:
        edge = typedef.Edge(u="A", v="B", cost="invalid", name=None)
        logger.error("✗ Should have failed: invalid cost type")
    except ValidationError:
        logger.info("✓ Invalid cost type correctly rejected")
    
    # Name too long
    try:
        long_name = "a" * 51
        edge = typedef.Edge(u="A", v="B", cost=None, name=long_name)
        logger.error("✗ Should have failed: name too long")
    except ValidationError:
        logger.info("✓ Name length validation works correctly")
    
    logger.info("")


def test_map_type_validation():
    """Test Map type validation"""
    logger.info("=" * 60)
    logger.info("Testing Map Type Validation")
    logger.info("=" * 60)
    
    # Valid map
    try:
        nodes = [
            typedef.Node(id="A", x=0, y=0, type="main", name=None, description=None),
            typedef.Node(id="B", x=1, y=0, type="nav", name=None, description=None)
        ]
        edges = [typedef.Edge(u="A", v="B", cost=None, name=None)]
        map_obj = typedef.Map(nodes=nodes, edges=edges)
        logger.info(f"✓ Valid map created with {len(map_obj.nodes)} nodes and {len(map_obj.edges)} edges")
    except ValidationError as e:
        logger.error(f"✗ Valid map creation failed: {e}")
    
    # Empty map
    try:
        map_obj = typedef.Map(nodes=[], edges=[])
        logger.info(f"✓ Empty map created")
    except ValidationError as e:
        logger.error(f"✗ Empty map creation failed: {e}")
    
    # Missing required fields
    try:
        map_obj = typedef.Map(nodes=[], edges=None)
        logger.error("✗ Should have failed: missing edges field")
    except ValidationError:
        logger.info("✓ Missing edges field correctly rejected")
    
    # Invalid nodes type
    try:
        map_obj = typedef.Map(nodes="invalid", edges=[])
        logger.error("✗ Should have failed: invalid nodes type")
    except ValidationError:
        logger.info("✓ Invalid nodes type correctly rejected")
    
    logger.info("")


def test_tree_node_type_validation():
    """Test TreeNode type validation"""
    logger.info("=" * 60)
    logger.info("Testing TreeNode Type Validation")
    logger.info("=" * 60)
    
    # Valid tree node without children
    try:
        tree_node = typedef.TreeNode(id="root", x=0, y=0, type="main", name=None, description=None, children=[])
        logger.info(f"✓ Valid tree node created: {tree_node.id} with {len(tree_node.children)} children")
    except ValidationError as e:
        logger.error(f"✗ Valid tree node creation failed: {e}")
    
    # Valid tree node with children
    try:
        child1 = typedef.TreeNode(id="child1", x=1, y=0, type="nav", name=None, description=None, children=[])
        child2 = typedef.TreeNode(id="child2", x=2, y=0, type="main", name=None, description=None, children=[])
        parent = typedef.TreeNode(id="parent", x=0, y=0, type="main", name=None, description=None, children=[child1, child2])
        logger.info(f"✓ Tree node with children created: {parent.id} with {len(parent.children)} children")
    except ValidationError as e:
        logger.error(f"✗ Tree node with children creation failed: {e}")
    
    # Nested tree structure
    try:
        leaf = typedef.TreeNode(id="leaf", x=3, y=0, type="nav", name=None, description=None, children=[])
        child = typedef.TreeNode(id="child", x=2, y=0, type="nav", name=None, description=None, children=[leaf])
        root = typedef.TreeNode(id="root", x=1, y=0, type="main", name=None, description=None, children=[child])
        logger.info(f"✓ Nested tree structure created with depth 3")
    except ValidationError as e:
        logger.error(f"✗ Nested tree creation failed: {e}")
    
    logger.info("")


# ============================================================================
# Function Tests
# ============================================================================

def test_load_map_from_str():
    """Test load_map_from_str function"""
    logger.info("=" * 60)
    logger.info("Testing load_map_from_str()")
    logger.info("=" * 60)
    
    # Valid JSON
    map_obj = tools.load_map_from_str(VALID_MAP_JSON)
    if map_obj:
        logger.info(f"✓ Valid JSON loaded: {len(map_obj.nodes)} nodes, {len(map_obj.edges)} edges")
    else:
        logger.error("✗ Valid JSON loading failed")
    
    # Invalid JSON syntax
    invalid_json = '{"nodes": [invalid]}'
    result = tools.load_map_from_str(invalid_json)
    if result is None:
        logger.info("✓ Invalid JSON syntax correctly returned None")
    else:
        logger.error("✗ Invalid JSON should return None")
    
    # Valid JSON but invalid schema
    invalid_schema = '{"nodes": "invalid", "edges": []}'
    result = tools.load_map_from_str(invalid_schema)
    if result is None:
        logger.info("✓ Invalid schema correctly returned None")
    else:
        logger.error("✗ Invalid schema should return None")
    
    # Empty string
    result = tools.load_map_from_str("")
    if result is None:
        logger.info("✓ Empty string correctly returned None")
    else:
        logger.error("✗ Empty string should return None")
    
    # Missing required fields
    missing_fields = '{"nodes": []}'
    result = tools.load_map_from_str(missing_fields)
    if result is None:
        logger.info("✓ Missing fields correctly returned None")
    else:
        logger.error("✗ Missing fields should return None")
    
    logger.info("")


def test_compute_costs():
    """Test compute_costs function"""
    logger.info("=" * 60)
    logger.info("Testing compute_costs()")
    logger.info("=" * 60)
    
    # Test with simple map
    map_obj = tools.load_map_from_str(SIMPLE_MAP_JSON)
    if map_obj:
        logger.info(f"Before compute_costs: edge cost = {map_obj.edges[0].cost}")
        tools.compute_costs(map_obj)
        # Distance from (0,0) to (3,4) is |3-0| + |4-0| = 7
        expected_cost = 7
        if map_obj.edges[0].cost == expected_cost:
            logger.info(f"✓ Cost computed correctly: {map_obj.edges[0].cost} (expected {expected_cost})")
        else:
            logger.error(f"✗ Cost computation failed: {map_obj.edges[0].cost} (expected {expected_cost})")
    
    # Test with complex map
    map_obj = tools.load_map_from_str(VALID_MAP_JSON)
    if map_obj:
        tools.compute_costs(map_obj)
        logger.info("✓ Complex map costs computed")
        for edge in map_obj.edges[:3]:  # Show first 3 edges
            logger.info(f"  Edge {edge.u_node}->{edge.v_node}: cost={edge.cost}")
    
    # Test with map with zero distance
    zero_dist_json = """{
        "nodes": [
            {"id": "A", "x": 5, "y": 5, "type": "main"},
            {"id": "B", "x": 5, "y": 5, "type": "main"}
        ],
        "edges": [{"u": "A", "v": "B"}]
    }"""
    map_obj = tools.load_map_from_str(zero_dist_json)
    if map_obj:
        tools.compute_costs(map_obj)
        if map_obj.edges[0].cost == 0:
            logger.info(f"✓ Zero distance handled correctly: cost={map_obj.edges[0].cost}")
        else:
            logger.error(f"✗ Zero distance failed: cost={map_obj.edges[0].cost}")
    
    logger.info("")


def test_check_map_validity():
    """Test check_map_validity function"""
    logger.info("=" * 60)
    logger.info("Testing check_map_validity()")
    logger.info("=" * 60)
    
    # Valid map with costs computed
    map_obj = tools.load_map_from_str(SIMPLE_MAP_JSON)
    if map_obj:
        tools.compute_costs(map_obj)
        result = tools.check_map_validity(map_obj)
        if result:
            logger.info("✓ Valid map passed validation")
        else:
            logger.error("✗ Valid map failed validation")
    
    # Map with missing node reference
    invalid_node_json = """{
        "nodes": [{"id": "A", "x": 0, "y": 0, "type": "main"}],
        "edges": [{"u": "A", "v": "B"}]
    }"""
    map_obj = tools.load_map_from_str(invalid_node_json)
    if map_obj:
        result = tools.check_map_validity(map_obj)
        if not result:
            logger.info("✓ Map with missing node reference correctly failed validation")
        else:
            logger.error("✗ Map with missing node should fail validation")
    
    # Map without computed costs
    map_obj = tools.load_map_from_str(SIMPLE_MAP_JSON)
    if map_obj:
        result = tools.check_map_validity(map_obj)
        if not result:
            logger.info("✓ Map without costs correctly failed validation")
        else:
            logger.error("✗ Map without costs should fail validation")
    
    # Map with zero cost
    map_obj = tools.load_map_from_str(SIMPLE_MAP_JSON)
    if map_obj:
        map_obj.edges[0].cost = 0
        result = tools.check_map_validity(map_obj)
        if not result:
            logger.info("✓ Map with zero cost correctly failed validation")
        else:
            logger.error("✗ Map with zero cost should fail validation")
    
    # Map with negative cost
    map_obj = tools.load_map_from_str(SIMPLE_MAP_JSON)
    if map_obj:
        map_obj.edges[0].cost = -5
        result = tools.check_map_validity(map_obj)
        if not result:
            logger.info("✓ Map with negative cost correctly failed validation")
        else:
            logger.error("✗ Map with negative cost should fail validation")
    
    # Empty map
    empty_map = typedef.Map(nodes=[], edges=[])
    result = tools.check_map_validity(empty_map)
    if result:
        logger.info("✓ Empty map passed validation")
    else:
        logger.error("✗ Empty map should pass validation")
    
    logger.info("")


def test_get_all_main_node_ids():
    """Test get_all_main_node_ids function"""
    logger.info("=" * 60)
    logger.info("Testing get_all_main_node_ids()")
    logger.info("=" * 60)
    
    # Map with main nodes
    map_obj = tools.load_map_from_str(VALID_MAP_JSON)
    if map_obj:
        main_nodes = tools.get_all_main_node_ids(map_obj)
        if main_nodes and len(main_nodes) == 3:  # A, C, E are main nodes
            logger.info(f"✓ Main nodes found: {main_nodes}")
        else:
            logger.error(f"✗ Expected 3 main nodes, got: {main_nodes}")
    
    # Map with no main nodes
    no_main_json = """{
        "nodes": [
            {"id": "A", "x": 0, "y": 0, "type": "nav"},
            {"id": "B", "x": 1, "y": 0, "type": "nav"}
        ],
        "edges": [{"u": "A", "v": "B"}]
    }"""
    map_obj = tools.load_map_from_str(no_main_json)
    if map_obj:
        main_nodes = tools.get_all_main_node_ids(map_obj)
        if main_nodes is None:
            logger.info("✓ Map with no main nodes correctly returned None")
        else:
            logger.error(f"✗ Should return None, got: {main_nodes}")
    
    # Map with only main nodes
    all_main_json = """{
        "nodes": [
            {"id": "A", "x": 0, "y": 0, "type": "main"},
            {"id": "B", "x": 1, "y": 0, "type": "main"},
            {"id": "C", "x": 2, "y": 0, "type": "main"}
        ],
        "edges": [{"u": "A", "v": "B"}, {"u": "B", "v": "C"}]
    }"""
    map_obj = tools.load_map_from_str(all_main_json)
    if map_obj:
        main_nodes = tools.get_all_main_node_ids(map_obj)
        if main_nodes and len(main_nodes) == 3:
            logger.info(f"✓ All main nodes map: {len(main_nodes)} nodes found")
        else:
            logger.error(f"✗ Expected 3 main nodes, got: {main_nodes}")
    
    # Empty map
    empty_map = typedef.Map(nodes=[], edges=[])
    main_nodes = tools.get_all_main_node_ids(empty_map)
    if main_nodes is None:
        logger.info("✓ Empty map correctly returned None")
    else:
        logger.error(f"✗ Empty map should return None, got: {main_nodes}")
    
    logger.info("")


def test_dijkstra_search():
    """Test dijkstra_search function"""
    logger.info("=" * 60)
    logger.info("Testing dijkstra_search()")
    logger.info("=" * 60)
    
    # Valid path
    map_obj = tools.load_map_from_str(VALID_MAP_JSON)
    if map_obj:
        tools.compute_costs(map_obj)
        path = tools.dijkstra_search("A", "E", map_obj)
        if path:
            logger.info(f"✓ Path found from A to E: {' -> '.join(path)}")
        else:
            logger.error("✗ Path should exist from A to E")
    
    # Path to self
    if map_obj:
        path = tools.dijkstra_search("A", "A", map_obj)
        if path and len(path) == 1 and path[0] == "A":
            logger.info(f"✓ Path to self correctly found: {path}")
        else:
            logger.error(f"✗ Path to self should be ['A'], got: {path}")
    
    # No path exists (disconnected graph)
    map_obj = tools.load_map_from_str(DISCONNECTED_MAP_JSON)
    if map_obj:
        tools.compute_costs(map_obj)
        path = tools.dijkstra_search("A", "C", map_obj)
        if path is None:
            logger.info("✓ No path correctly returned None")
        else:
            logger.error(f"✗ Should return None for disconnected nodes, got: {path}")
    
    # Invalid start node
    map_obj = tools.load_map_from_str(SIMPLE_MAP_JSON)
    if map_obj:
        tools.compute_costs(map_obj)
        path = tools.dijkstra_search("Z", "Y", map_obj)
        if path is None:
            logger.info("✓ Invalid start node correctly returned None")
        else:
            logger.error(f"✗ Invalid start node should return None, got: {path}")
    
    # Invalid end node
    if map_obj:
        path = tools.dijkstra_search("X", "Z", map_obj)
        if path is None:
            logger.info("✓ Invalid end node correctly returned None")
        else:
            logger.error(f"✗ Invalid end node should return None, got: {path}")
    
    # Complex path
    map_obj = tools.load_map_from_str(VALID_MAP_JSON)
    if map_obj:
        tools.compute_costs(map_obj)
        path = tools.dijkstra_search("A", "C", map_obj)
        if path:
            logger.info(f"✓ Complex path found: {' -> '.join(path)} (length: {len(path)})")
        else:
            logger.error("✗ Path should exist from A to C")
    
    logger.info("")


def test_translate_graph_to_tree():
    """Test translate_graph_to_tree function"""
    logger.info("=" * 60)
    logger.info("Testing translate_graph_to_tree()")
    logger.info("=" * 60)
    
    # Valid tree conversion
    map_obj = tools.load_map_from_str(VALID_MAP_JSON)
    if map_obj:
        tree = tools.translate_graph_to_tree(map_obj, "A")
        if tree and tree.id == "A":
            logger.info(f"✓ Tree created with root: {tree.id}, children: {len(tree.children)}")
        else:
            logger.error("✗ Tree creation failed")
    
    # Different root node
    if map_obj:
        tree = tools.translate_graph_to_tree(map_obj, "B")
        if tree and tree.id == "B":
            logger.info(f"✓ Tree created with root B, children: {len(tree.children)}")
        else:
            logger.error("✗ Tree creation with root B failed")
    
    # Invalid root node
    if map_obj:
        tree = tools.translate_graph_to_tree(map_obj, "Z")
        if tree is None:
            logger.info("✓ Invalid root node correctly returned None")
        else:
            logger.error(f"✗ Invalid root should return None, got tree with root: {tree.id}")
    
    # Simple linear graph
    map_obj = tools.load_map_from_str(SIMPLE_MAP_JSON)
    if map_obj:
        tree = tools.translate_graph_to_tree(map_obj, "X")
        if tree and tree.id == "X" and len(tree.children) == 1:
            logger.info(f"✓ Linear graph converted: {tree.id} -> {tree.children[0].id}")
        else:
            logger.error("✗ Linear graph conversion failed")
    
    # Check tree structure integrity
    map_obj = tools.load_map_from_str(VALID_MAP_JSON)
    if map_obj:
        tree = tools.translate_graph_to_tree(map_obj, "A")
        if tree:
            # Count all nodes in tree
            def count_nodes(node):
                return 1 + sum(count_nodes(child) for child in node.children)
            node_count = count_nodes(tree)
            logger.info(f"✓ Tree contains {node_count} nodes (original graph: {len(map_obj.nodes)} nodes)")
    
    logger.info("")


def test_validate_path():
    """Test validate_path function"""
    logger.info("=" * 60)
    logger.info("Testing validate_path()")
    logger.info("=" * 60)
    
    # Valid path
    map_obj = tools.load_map_from_str(VALID_MAP_JSON)
    if map_obj:
        tools.compute_costs(map_obj)
        path = ["A", "B", "C"]
        result = tools.validate_path(map_obj, path)
        if result:
            logger.info(f"✓ Valid path accepted: {' -> '.join(path)}")
        else:
            logger.error(f"✗ Valid path rejected: {' -> '.join(path)}")
    
    # Invalid path (nodes not connected)
    if map_obj:
        path = ["A", "C"]  # A and C are not directly connected in tree
        result = tools.validate_path(map_obj, path)
        if not result:
            logger.info(f"✓ Invalid path correctly rejected: {' -> '.join(path)}")
        else:
            logger.error(f"✗ Invalid path should be rejected: {' -> '.join(path)}")
    
    # Single node path
    if map_obj:
        path = ["A"]
        result = tools.validate_path(map_obj, path)
        if result:
            logger.info(f"✓ Single node path accepted: {path}")
        else:
            logger.error(f"✗ Single node path rejected: {path}")
    
    # Empty path
    if map_obj:
        path = []
        result = tools.validate_path(map_obj, path)
        if not result:
            logger.info("✓ Empty path correctly rejected")
        else:
            logger.error("✗ Empty path should be rejected")
    
    # Path with non-existent node
    if map_obj:
        path = ["A", "Z"]
        result = tools.validate_path(map_obj, path)
        if not result:
            logger.info("✓ Path with non-existent node correctly rejected")
        else:
            logger.error("✗ Path with non-existent node should be rejected")
    
    # Valid longer path
    if map_obj:
        path = ["A", "B", "D", "E"]
        result = tools.validate_path(map_obj, path)
        if result:
            logger.info(f"✓ Valid longer path accepted: {' -> '.join(path)}")
        else:
            logger.error(f"✗ Valid longer path rejected: {' -> '.join(path)}")
    
    # Map without costs (invalid map)
    map_obj = tools.load_map_from_str(SIMPLE_MAP_JSON)
    if map_obj:
        path = ["X", "Y"]
        result = tools.validate_path(map_obj, path)
        if not result:
            logger.info("✓ Path on invalid map (no costs) correctly rejected")
        else:
            logger.error("✗ Path on invalid map should be rejected")
    
    logger.info("")


# ============================================================================
# Integration Tests
# ============================================================================

def test_full_workflow():
    """Test complete workflow: load -> compute -> validate -> search"""
    logger.info("=" * 60)
    logger.info("Testing Full Workflow Integration")
    logger.info("=" * 60)
    
    # Load map
    logger.info("[Step 1] Loading map from JSON...")
    map_obj = tools.load_map_from_str(VALID_MAP_JSON)
    if not map_obj:
        logger.error("✗ Failed to load map")
        return
    logger.info(f"✓ Map loaded: {len(map_obj.nodes)} nodes, {len(map_obj.edges)} edges")
    
    # Compute costs
    logger.info("[Step 2] Computing edge costs...")
    tools.compute_costs(map_obj)
    logger.info(f"✓ Costs computed")
    
    # Validate map
    logger.info("[Step 3] Validating map...")
    if tools.check_map_validity(map_obj):
        logger.info("✓ Map is valid")
    else:
        logger.error("✗ Map validation failed")
        return
    
    # Get main nodes
    logger.info("[Step 4] Getting main nodes...")
    main_nodes = tools.get_all_main_node_ids(map_obj)
    if main_nodes:
        logger.info(f"✓ Found {len(main_nodes)} main nodes: {main_nodes}")
    else:
        logger.warning("⚠ No main nodes found")
    
    # Find path
    logger.info("[Step 5] Finding shortest path...")
    if main_nodes and len(main_nodes) >= 2:
        start, end = main_nodes[0], main_nodes[-1]
        path = tools.dijkstra_search(start, end, map_obj)
        if path:
            logger.info(f"✓ Path found: {' -> '.join(path)}")
            
            # Validate the path
            logger.info("[Step 6] Validating path...")
            if tools.validate_path(map_obj, path):
                logger.info("✓ Path is valid")
            else:
                logger.warning("⚠ Path validation returned False")
        else:
            logger.warning(f"⚠ No path found from {start} to {end}")
    
    # Convert to tree
    logger.info("[Step 7] Converting graph to tree...")
    if main_nodes:
        tree = tools.translate_graph_to_tree(map_obj, main_nodes[0])
        if tree:
            logger.info(f"✓ Tree created with root: {tree.id}")
        else:
            logger.error("✗ Tree conversion failed")
    
    logger.info("")


def test_edge_cases():
    """Test edge cases and boundary conditions"""
    logger.info("=" * 60)
    logger.info("Testing Edge Cases")
    logger.info("=" * 60)
    
    # Single node map
    single_node_json = """{
        "nodes": [{"id": "A", "x": 0, "y": 0, "type": "main"}],
        "edges": []
    }"""
    map_obj = tools.load_map_from_str(single_node_json)
    if map_obj:
        logger.info("✓ Single node map loaded")
        path = tools.dijkstra_search("A", "A", map_obj)
        if path == ["A"]:
            logger.info("✓ Path to self in single node map works")
    
    # Large coordinates
    large_coord_json = """{
        "nodes": [
            {"id": "A", "x": 1000000, "y": 1000000, "type": "main"},
            {"id": "B", "x": 1000001, "y": 1000001, "type": "main"}
        ],
        "edges": [{"u": "A", "v": "B"}]
    }"""
    map_obj = tools.load_map_from_str(large_coord_json)
    if map_obj:
        tools.compute_costs(map_obj)
        logger.info(f"✓ Large coordinates handled: cost={map_obj.edges[0].cost}")
    
    # Negative coordinates
    negative_coord_json = """{
        "nodes": [
            {"id": "A", "x": -10, "y": -10, "type": "main"},
            {"id": "B", "x": 10, "y": 10, "type": "main"}
        ],
        "edges": [{"u": "A", "v": "B"}]
    }"""
    map_obj = tools.load_map_from_str(negative_coord_json)
    if map_obj:
        tools.compute_costs(map_obj)
        expected = 40  # |10-(-10)| + |10-(-10)| = 40
        if map_obj.edges[0].cost == expected:
            logger.info(f"✓ Negative coordinates handled: cost={map_obj.edges[0].cost}")
    
    # Floating point coordinates
    float_coord_json = """{
        "nodes": [
            {"id": "A", "x": 1.5, "y": 2.7, "type": "main"},
            {"id": "B", "x": 4.2, "y": 6.1, "type": "main"}
        ],
        "edges": [{"u": "A", "v": "B"}]
    }"""
    map_obj = tools.load_map_from_str(float_coord_json)
    if map_obj:
        tools.compute_costs(map_obj)
        logger.info(f"✓ Floating point coordinates handled: cost={map_obj.edges[0].cost}")
    
    # Very long node IDs
    long_id_json = """{
        "nodes": [
            {"id": "very_long_node_identifier_123456789", "x": 0, "y": 0, "type": "main"},
            {"id": "another_very_long_node_identifier_987654321", "x": 1, "y": 0, "type": "main"}
        ],
        "edges": [{"u": "very_long_node_identifier_123456789", "v": "another_very_long_node_identifier_987654321"}]
    }"""
    map_obj = tools.load_map_from_str(long_id_json)
    if map_obj:
        logger.info("✓ Very long node IDs handled")
    
    logger.info("")


# ============================================================================
# Real Map Test (using small1.map.json)
# ============================================================================

def test_real_map():
    """Test with actual map file"""
    logger.info("=" * 60)
    logger.info("Testing with Real Map Data (small1.map.json)")
    logger.info("=" * 60)
    
    try:
        with open("/home/n1ghts4kura/Desktop/ufc-2026/backend/assets/small1.map.json", "r", encoding="utf-8") as f:
            json_str = f.read()
        
        logger.info("✓ Map file loaded")
        
        # Parse map
        map_obj = tools.load_map_from_str(json_str)
        if not map_obj:
            logger.error("✗ Failed to parse map")
            return
        logger.info(f"✓ Map parsed: {len(map_obj.nodes)} nodes, {len(map_obj.edges)} edges")
        
        # Compute costs
        tools.compute_costs(map_obj)
        logger.info("✓ Costs computed")
        
        # Validate
        if tools.check_map_validity(map_obj):
            logger.info("✓ Map is valid")
        else:
            logger.error("✗ Map validation failed")
            return
        
        # Get main nodes
        main_nodes = tools.get_all_main_node_ids(map_obj)
        if main_nodes:
            logger.info(f"✓ Found {len(main_nodes)} main nodes")
            logger.info(f"  First few: {main_nodes[:5]}")
        
        # Test pathfinding between two main nodes
        if main_nodes and len(main_nodes) >= 2:
            start, end = "registration_center", "emergency_room"
            logger.info(f"Finding path from {start} to {end}...")
            path = tools.dijkstra_search(start, end, map_obj)
            if path:
                logger.info(f"✓ Path found with {len(path)} nodes")
                logger.info(f"  Path: {' -> '.join(path)}")
            else:
                logger.warning(f"⚠ No path found")
        
        # Test tree conversion
        if main_nodes:
            tree = tools.translate_graph_to_tree(map_obj, main_nodes[0])
            if tree:
                logger.info(f"✓ Tree created from root: {tree.id}")
    
    except FileNotFoundError:
        logger.warning("⚠ Map file not found, skipping real map test")
    except Exception as e:
        logger.error(f"✗ Real map test failed: {e}", exc_info=True)
    
    logger.info("")


# ============================================================================
# Main Test Runner
# ============================================================================

def run_all_tests():
    """Run all test suites"""
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 15 + "MAP MODULE TEST SUITE" + " " * 22 + "║")
    logger.info("╚" + "=" * 58 + "╝")
    logger.info("")
    
    # Type validation tests
    test_node_type_validation()
    test_edge_type_validation()
    test_map_type_validation()
    test_tree_node_type_validation()
    
    # Function tests
    test_load_map_from_str()
    test_compute_costs()
    test_check_map_validity()
    test_get_all_main_node_ids()
    test_dijkstra_search()
    test_translate_graph_to_tree()
    test_validate_path()
    
    # Integration tests
    test_full_workflow()
    test_edge_cases()
    test_real_map()
    
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 18 + "ALL TESTS COMPLETED" + " " * 21 + "║")
    logger.info("╚" + "=" * 58 + "╝")


if __name__ == "__main__":
    # Setup logging
    logger.setup_file_logging("/home/n1ghts4kura/Desktop/ufc-2026/backend/logs")
    
    # Run all tests
    run_all_tests()


