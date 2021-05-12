const { typeAssert } = require('./typeAssert.umd')

const customClj = (number) => {
    if (typeof number === 'number' && number > 500) {
        return true
    }
    return 'number less than 500'
}

try {
    typeAssert(114, 'number') // pass
    typeAssert('514', 'string') // pass
    typeAssert(null, 'number?') // pass
    typeAssert(null, null) // pass
    typeAssert(undefined, 'undefined') // pass

    typeAssert(new Date(), 'Date') // pass
    typeAssert(new Date(), 'object') // also pass, `Date` is also `Object`
    typeAssert(/-/, 'RegExp') // pass
    typeAssert(new RegExp(), 'RegExp') // pass

    typeAssert([1, '2', [3]], 'Array') // pass
    typeAssert([1, '2', [3]], []) // pass
    typeAssert([1, 2, 3], ['number']) // pass
    typeAssert([160, null, 95], ['number?']) // pass
    typeAssert([123, '456'], [ 'number'.sumWith('string') ]) // pass
    typeAssert(
        [123, '456', { 'data': 789 }, new Date()],
        [ 'number'.sumWith('string').sumWith({}.sumWith('Date')) ]
    ) // pass

    typeAssert(512, customClj) // pass

    typeAssert({}, 'object') // pass
    typeAssert({}, {}) // pass
    typeAssert({ a: 5, b: '10' }, { a: 'number', b: 'string' }) // pass
    typeAssert({
        a: [1, 2, 3],
        b: [4, { 'data': 5 }, 6],
        c: ['7', '8', null, 9],
        d: 'fields not specified will not be checked'
    }, {
        a: [ 'number' ],
        b: [ 'number'.sumWith({ 'data': 'number' }) ],
        c: [ 'string?'.sumWith('number') ]
    }) // pass

    typeAssert([ null, { x: 15 } ], [ { x: 'number' }.orNull() ]) // pass
} catch (error) {
    console.error(error)
    throw 'test failed'
}

try { ({}).orNull().orNull() } catch (error) {
    if (error !== 'Type assertion failed: "<onbuild> Object.prototype.orNull": trying to nest nullable modification') throw 'test failed'
}

try { 'undefined'.orNull() } catch (error) {
    if (error !== 'Type assertion failed: "<onbuild> String.prototype.orNull": "undefined" type cannot be nullable') throw 'test failed'
}

try { 'string'.orNull().orNull() } catch (error) {
    if (error !== 'Type assertion failed: "<onbuild> String.prototype.orNull": trying to nest nullable modification') throw 'test failed'
}

try { typeAssert(911, new Date()) } catch (error) {
    if (error !== 'Type assertion failed: "object": invalid assertion') throw 'test failed'
}

try { typeAssert(114, 'string') } catch (error) {
    if (error !== 'Type assertion failed: "object": expected type "string", got "number"') throw 'test failed'
}

try { typeAssert('514', 'number') } catch (error) {
    if (error !== 'Type assertion failed: "object": expected type "number", got "string"') throw 'test failed'
}

try { typeAssert(null, 'object') } catch (error) {
    if (error !== 'Type assertion failed: "object": unexpected "null" value') throw 'test failed'
}

try { typeAssert(null, 'undefined?') } catch (error) {
    if (error !== 'Type assertion failed: "object": "undefined" type cannot be nullable') throw 'test failed'
}

try {
    typeAssert(192, customClj)
} catch (error) {
    if (error !== 'Type assertion failed: "object": number less than 500') throw 'test failed'
}

try { typeAssert({}, null) } catch (error) {
    if (error !== 'Type assertion failed: "object": expected "null" value, got "object"') throw 'test failed'
}

try { typeAssert({ a: null }, { a: { b: 15 } }) } catch (error) {
    if (error !== 'Type assertion failed: "object.a": unexpected "null" value') throw 'test failed'
}

try { typeAssert({}, { a: {} }) } catch (error) {
    if (error !== 'Type assertion failed: "object.a": unexpected "undefined" value') throw 'test failed'
}

try { typeAssert(/-/, 'Date') } catch (error) {
    if (error !== 'Type assertion failed: "object": expected type "Date", checking using ctor "Date", got "RegExp"') throw 'test failed'
}

try { typeAssert(/-/, 'Array') } catch (error) {
    if (error !== 'Type assertion failed: "object": expected type "Array", checking using ctor "Array", got "RegExp"') throw 'test failed'
}

try { typeAssert(new Date(), 'RegExp') } catch (error) {
    if (error !== 'Type assertion failed: "object": expected type "RegExp", checking using ctor "RegExp", got "Date"') throw 'test failed'
}

try { typeAssert(['123', '456'], ['string', 'object']) } catch (error) {
    if (error !== 'Type assertion failed: "object": "array" type assertion should only have one element') throw 'test failed'
}

try { typeAssert([ '123', 456 ], [ 'string'.sumWith('object') ]) } catch (error) {
    const err = `
Type assertion failed: "object[1]": sum type check failure:
  - branch 0 faild for: { Type assertion failed: "object[1]": expected type "string", got "number" }
  - branch 1 faild for: { Type assertion failed: "object[1]": expected type "object", got "number" }
    `
    if (error.trim() !== err.trim()) throw 'test failed'
}
