// Test 11: Arrow function with destructured params - specifically tests paren-depth tracking
// This is the core fix from Round 3 - no JSX closing tags, no template literals
const processItems = ({ items, options }) => {
    const result = items.map(item => {
        return item * options.multiplier;
    });
    return result;
};

// Another destructured function
function handleClick({ target, currentTarget }) {
    console.log(target);
    return currentTarget;
}
