const fs = require('fs');
const path = require('path');
const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;

const filePath = process.argv[2];

if (!filePath) {
    console.error("Please provide a file path.");
    process.exit(1);
}

try {
    const code = fs.readFileSync(filePath, 'utf-8');
    
    // Parse using Babel AST
    const ast = parser.parse(code, {
        sourceType: 'unambiguous',
        plugins: [
            'jsx',
            'typescript',
            'decorators-legacy',
            'classProperties'
        ]
    });

    const toc = {
        functions: [],
        classes: [],
        variables: []
    };

    traverse(ast, {
        FunctionDeclaration(p) {
            const name = p.node.id ? p.node.id.name : 'anonymous';
            const params = p.node.params.map(param => param.name || (param.type === 'ObjectPattern' ? '{...}' : 'param')).join(', ');
            const start = p.node.loc.start.line;
            const end = p.node.loc.end.line;
            toc.functions.push(`- \`${name}(${params})\` (Lines ${start}-${end})`);
        },
        VariableDeclarator(p) {
            // Check if variable is holding a function (e.g. React functional components)
            if (p.node.init && (p.node.init.type === 'ArrowFunctionExpression' || p.node.init.type === 'FunctionExpression')) {
                const name = p.node.id.name || 'anonymous';
                const params = p.node.init.params.map(param => {
                    if (param.type === 'Identifier') return param.name;
                    if (param.type === 'ObjectPattern') return '{...}';
                    if (param.type === 'ArrayPattern') return '[...]';
                    return 'param';
                }).join(', ');
                const start = p.node.init.loc.start.line;
                const end = p.node.init.loc.end.line;
                toc.functions.push(`- \`${name}(${params})\` (Lines ${start}-${end})`);
            } else if (p.parent && p.parent.parent && p.parent.parent.type === 'Program') {
                // Record global/top-level state or constants
                const name = p.node.id.name;
                const start = p.node.loc.start.line;
                if (name) toc.variables.push(`- \`${name}\` (Line ${start})`);
            }
        },
        ClassDeclaration(p) {
            const name = p.node.id ? p.node.id.name : 'anonymous';
            const start = p.node.loc.start.line;
            const end = p.node.loc.end.line;
            toc.classes.push(`- \`${name}\` (Lines ${start}-${end})`);
        }
    });

    console.log(`\n### 📖 Table of Contents (TOC) for \`${path.basename(filePath)}\``);
    
    if (toc.classes.length > 0) {
        console.log("\n**🏛️ Classes:**");
        toc.classes.forEach(c => console.log(c));
    }
    if (toc.functions.length > 0) {
        console.log("\n**⚙️ Functions / Components:**");
        toc.functions.forEach(f => console.log(f));
    }
    if (toc.variables.length > 0) {
        console.log("\n**📦 Top-Level Variables:**");
        toc.variables.forEach(v => console.log(v));
    }
    
    console.log("\n💡 *AI Hint: Use the native `view_file` tool with the specific StartLine and EndLine to read only the function you need, saving thousands of tokens!*");

} catch (err) {
    console.error(`Failed to parse AST for ${filePath}. Error: ${err.message}`);
}
