section .data
    fmt_scan db "Memory scan at address %016lx: %02x", 10, 0
    fmt_pattern db "Pattern detected at %016lx", 10, 0

section .text
    global memory_scan
    extern printf

memory_scan:
    push rbp
    mov rbp, rsp
    
    ; Parameters:
    ; rdi = start address
    ; rsi = length
    ; rdx = pattern to search
    
    mov r12, rdi        ; Store start address
    mov r13, rsi        ; Store length
    mov r14, rdx        ; Store pattern
    
    xor rcx, rcx        ; Initialize counter
    
scan_loop:
    cmp rcx, r13
    jge scan_done
    
    mov al, [r12 + rcx]
    
    ; Log current byte
    push rcx
    lea rdi, [fmt_scan]
    mov rsi, r12
    add rsi, rcx
    movzx rdx, al
    xor rax, rax
    call printf
    pop rcx
    
    ; Check for pattern match
    cmp al, r14b
    jne continue_scan
    
    ; Pattern found
    push rcx
    lea rdi, [fmt_pattern]
    mov rsi, r12
    add rsi, rcx
    xor rax, rax
    call printf
    pop rcx
    
continue_scan:
    inc rcx
    jmp scan_loop
    
scan_done:
    mov rsp, rbp
    pop rbp
    ret