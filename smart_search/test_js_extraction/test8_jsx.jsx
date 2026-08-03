// Test 8: JSX file with braces used for expressions
import React from 'react';

function JSXComponent({ items }) {
    return (
        <div className="container">
            <h1>Items List</h1>
            <ul>
                {items.map(item => (
                    <li key={item.id}>{item.name}</li>
                ))}
            </ul>
        </div>
    );
}

export default JSXComponent;
