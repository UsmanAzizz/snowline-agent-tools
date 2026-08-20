// Test 8: JSX with destructured props - should now work with paren-depth tracking
import React from 'react';

function JSXComponent({ title, items }) {
    return (
        <div className="container">
            <h1>{title}</h1>
            <ul>
                {items.map(item => (
                    <li key={item.id}>{item.name}</li>
                ))}
            </ul>
        </div>
    );
}

export default JSXComponent;
