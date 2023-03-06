Calculator-plusplus
------

A fork of the original [simple calculator](https://github.com/TISUnion/Calculator) with advanced features

Requires: [MCDReforged](https://github.com/Fallen-Breath/MCDReforged) >= `2.1.0` and [simpleeval](https://pypi.org/project/simpleeval/)

## Usage

### variables: 

use `==set (variable_name):(value or expression)` to define a variable, once created, you can reference it with a `$` prefix, variables with a expression will be calculated every time. eg:

```
==set test:123
>test: 123
==$test+321
>444

==set test2:$test+321
==set $test:321
==$test2 + 1
>643
```

or directly access it with `==get (variable_name)`

Attention: using something such as `==$(some variable name)` will return a result after calculated, and it will ALSO be recorded into history, so if you donn't want to mess up with history or you want to access a variable with expressions, do `==get (variable_name)`

### history:

calculation history is stored in a special variable, you can reference it with simply a number, eg:`$0` is the last result, and `$1` is the result before, etc.

### stack calculator:

just use `==stack (expression)` , explains itself.

<details>
<summary>HACKY STUFF</summary>
<br>
there's some internal variables for you guys to play with:<br>
`_MAX_DEPTH`: maximum call depth for a expression, prevents endless looping<br>
`_STACK_SHULKERS`: use shulker boxes for stack calculator? set to 0 to disable shulker boxes in stack calculator, basically made for myself playing GT:NH(very hardcore tech pack on 1.7.10, absolutely recommended for you guys if you want to take a break from technical minecraft)<br>
`_STACK_BASE`: in case you want to calculate items that is not 64 stacked like enderpearls, or even snowballs ig?<br>
</details>