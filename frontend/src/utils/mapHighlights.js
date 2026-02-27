/**
 * 地图高亮计算引擎
 *
 * 基于导航命令和地图原始数据计算需要高亮显示的节点和边。
 */

/**
 * 从commands中提取路径节点ID序列
 * @param {Object} commands - 解析后的导航命令
 * @returns {string[]} 路径节点ID数组
 */
function extractPathFromCommands(commands) {
  const pathNodeIds = [];

  if (!commands || !commands.commands || !Array.isArray(commands.commands)) {
    console.warn('Invalid commands format for path extraction');
    return pathNodeIds;
  }

  // 假设 commands.commands 是 Command 对象数组
  // Command: { action: string, target: string, direction?: string }
  // 我们提取所有唯一的 target 值作为路径节点
  const commandList = commands.commands;

  for (const cmd of commandList) {
    if (cmd.target && !pathNodeIds.includes(cmd.target)) {
      pathNodeIds.push(cmd.target);
    }
  }

  return pathNodeIds;
}

/**
 * 判断边是否在路径中
 * @param {Object} edge - 地图边对象
 * @param {string[]} pathNodeIds - 路径节点ID序列
 * @returns {boolean} 边是否在路径中
 */
function isEdgeInPath(edge, pathNodeIds) {
  if (!edge || !pathNodeIds || !Array.isArray(pathNodeIds)) {
    return false;
  }

  // 边在路径中，当且仅当：
  // 1. source 和 target 都在 pathNodeIds 中
  // 2. source 和 target 在 pathNodeIds 中是相邻的（按顺序）
  const sourceIndex = pathNodeIds.indexOf(edge.source);
  const targetIndex = pathNodeIds.indexOf(edge.target);

  // 两个节点都在路径中且相邻
  return sourceIndex !== -1 &&
         targetIndex !== -1 &&
         Math.abs(sourceIndex - targetIndex) === 1;
}

/**
 * 基于 commands 和地图数据计算高亮状态
 * @param {Object} commands - 解析后的导航命令
 * @param {Object} mapData - 地图原始数据（包含 nodes 和 edges）
 * @returns {Object} highlightedMap - 包含 highlight 属性的增强地图
 */
export function computeHighlights(commands, mapData) {
  // 参数验证
  if (!mapData || !mapData.nodes || !Array.isArray(mapData.nodes)) {
    console.error('Invalid mapData format: missing nodes array');
    return { nodes: [], edges: [] };
  }

  if (!mapData.edges || !Array.isArray(mapData.edges)) {
    console.error('Invalid mapData format: missing edges array');
    return { nodes: mapData.nodes || [], edges: [] };
  }

  // 1. 解析 commands 获取路径节点序列
  const pathNodeIds = extractPathFromCommands(commands);

  // 如果没有有效的路径，返回原始数据但所有highlight为false
  if (pathNodeIds.length === 0) {
    return {
      nodes: mapData.nodes.map(node => ({
        ...node,
        highlight: false
      })),
      edges: mapData.edges.map(edge => ({
        ...edge,
        highlight: false
      }))
    };
  }

  // 2. 为每个节点添加 highlight 属性
  const highlightedNodes = mapData.nodes.map(node => ({
    ...node,
    highlight: pathNodeIds.includes(node.id)
  }));

  // 3. 为每条边添加 highlight 属性
  const highlightedEdges = mapData.edges.map(edge => ({
    ...edge,
    highlight: isEdgeInPath(edge, pathNodeIds)
  }));

  return {
    nodes: highlightedNodes,
    edges: highlightedEdges
  };
}

/**
 * 调试函数：打印高亮地图信息
 * @param {Object} highlightedMap - 高亮地图数据
 */
export function debugHighlightedMap(highlightedMap) {
  if (!highlightedMap) {
    console.log('Highlighted map is null or undefined');
    return;
  }

  const highlightedNodes = highlightedMap.nodes?.filter(n => n.highlight) || [];
  const highlightedEdges = highlightedMap.edges?.filter(e => e.highlight) || [];

  console.log('Highlighted Map Info:');
  console.log(`- Total nodes: ${highlightedMap.nodes?.length || 0}`);
  console.log(`- Highlighted nodes: ${highlightedNodes.length}`);
  console.log(`- Total edges: ${highlightedMap.edges?.length || 0}`);
  console.log(`- Highlighted edges: ${highlightedEdges.length}`);

  if (highlightedNodes.length > 0) {
    console.log('Highlighted nodes:', highlightedNodes.map(n => ({ id: n.id, name: n.name })));
  }

  if (highlightedEdges.length > 0) {
    console.log('Highlighted edges:', highlightedEdges.map(e => ({ source: e.source, target: e.target })));
  }
}

export default {
  computeHighlights,
  debugHighlightedMap
};