function getNetworkData() {
  let networkData = [];

  // Get all network requests
  let entries = window.performance.getEntriesByType("resource");

  // Filter and extract network data
  for (let i = 0; i < entries.length; i++) {
    let entry = entries[i];

      // Create an object with URL, type, and size
      let data = {
        URL: entry.name,
        Type: entry.initiatorType,
        Size: entry.transferSize
      };

      networkData.push(data);
  }

  // Return the network data as a JSON object
  let json_data = JSON.stringify(networkData)
  console.log(json_data);
  return json_data;
}

return getNetworkData();

