function getFontFamilies() {
  // Select all p, h, and a tags on the page
  let elements = document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, a');

  // Define a list to store unique font families
  let fontFamilies = [];

  // Iterate through the selected elements
  elements.forEach(element => {
    // Get the computed style of the element
    let computedStyle = getComputedStyle(element);

    // Get the font family from the computed style
    let fontFamily = computedStyle.fontFamily;

    // Check if the font family is not already in the list
    if (!fontFamilies.includes(fontFamily)) {
      // Add the font family to the list
      fontFamilies.push(fontFamily);
    }
  });

  console.log(fontFamilies);
  return fontFamilies;
}

return getFontFamilies();
