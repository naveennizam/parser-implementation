###################################################
### CONSTANT
###################################################



from secrets import token_bytes


DIGITS = '01234567689'

###################################################
### ERROR
###################################################
class Error:
    def __init__(self,error_name,details,pos_start,pos_end):
        self.error_name  = error_name
        self.details = details
        self.pos_start = pos_start
        self.pos_end = pos_end
        
    def as_string(self):

        result = f'{self.error_name}:{self.details}'
        #result += f'File{self.fn},line{self.ln+1}'
        return result

class IllegalCharError(Error):
    def __init__(self, details,pos_start,pos_end):
        super().__init__(pos_start,pos_end, 'Illegal Character',details)
        
###################################################
### POSITION
###################################################

class Position:
    def __init__(self,idx,ln,col,fn,ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self,current_char=None):
        self.idx += 1
        self.col += 1

        if current_char == '\n':
            self.idx += 1
            self.col += 0
        return self

    def copy(self):
        return Position(self.idx,self.ln,self.col,self.fn,self.ftxt)



###################################################
### TOKEN
###################################################



TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_LPAREN ='LPAREN'  #(
TT_RPAREN = 'RPAREN'  #)
TT_GT = 'GT'
TT_LT = 'LT'
TT_LTE = 'LTE'
TT_GTE = 'GTE'
TT_EOF = 'EOF'
TT_NE = 'NE'
TT_EQ = 'EQ'
KEYWORDS = [
    'VAR','AND','OR','NOT'
]

class Token:
    def __init__(self,type_,value=None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'

###################################################
### LEXER
###################################################

class Lexer:
    def __init__(self,fn,text):
        self.text = text
        self.fn = fn 
        self.pos = Position(-1,0,-1,fn,text)
        self.current_char = None
        self.advance()
        
    def advance(self):
        self.pos.advance (self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len (self.text) else None
       
    def make_tokens(self):
        tokens = []
        while self.current_char != None:
            if self.current_char in ' ':
                self.advance( )
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN))
                self.advance()
            elif self.current_char == '!':
                tokens.append(Token(TT_NE))
                self.advance()

            elif self.current_char == '<':
                #tokens.append(Token(TT_LT))
                tokens.append(self.less_than())
                self.advance()
            elif self.current_char == '>':
                #tokens.append(Token(TT_GT))
                tokens.append(self.greater_than())
                self.advance()
                
            
            else:
                #return some error
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [] , IllegalCharError(pos_start,self.pos,"'" + char + "'")
            
        return tokens,None

    def make_number(self):
        num_str = ' '
        dot_count = 0

        while self.current_char != None and self.current_char in DIGITS + '.' :
            if self.current_char == '.':
                if dot_count == 1 : break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()
            
        if dot_count ==0:
            return Token(TT_INT, int(num_str))
        else:
            return Token(TT_FLOAT, float(num_str))

    # def make_identifier(self):
    #     id_str = ' '
    #     pos_start = self.pos.copy()

    #     while self.current_char != None and self.current_char in LETTER_DIGITS + '_':
    #         id_str += self.current_char
    #         self.advance()
        
    #     tok.type = TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER
    #     return Token(TT_NE,pos_start=pos_start,self.pos)



    # def less_than(self):
    #     tok_type = TT__LT
    #     pos_start = self.pos.copy()
    #     self.advance()
    #     if self.current_char == '<':
    #         self.advance()
    #         tok_type =TT_LTE
    #     return Token(tok_type,pos_start=pos_start,pos_end=self.pos)

    # def greater_than(self):
    #     tok_type = TT__GT
    #     pos_start = self.pos.copy()
    #     self.advance()
    #     if self.current_char == '>':
    #         self.advance()
    #         tok_type =TT_GTE
    #     return Token(tok_type,pos_start=pos_start,pos_end=self.pos)

###################################################
######### NODES
###################################################
class NumberNode:
    def __init__(self, tok):
        self.tok = tok

    def __repr__ (self):
        return f'{self.tok}'
class Bin0pNode:
    def __init__ (self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node

    def __repr__ (self):
        return f'({self.left_node},{self.op_tok},{self.right_node})'


###################################################
###### PARSER
###################################################
class Parser:
    def __init__(self,tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self):
        
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
            
        return self.current_tok
     ###################################################

    def parse(self):
        res = self.expr()
        return res



    def factor(self):
        tok = self.current_tok
        if tok.type in ((TT_INT, TT_FLOAT)):
            self.advance()
            return NumberNode(tok)

    def term(self):
        return self.bin_op(self.factor,(TT_MUL, TT_DIV))


    def expr(self):
        return self.bin_op(self.term,(TT_PLUS, TT_MINUS))



    def bin_op(self,func,ops):
        left = func()
        while self.current_tok.type in ops:
            op_tok = self.current_tok
            right = func()
            left = Bin0pNode(left, op_tok , right)
            self.advance()
        return left




###################################################
### RUN
###################################################
    
def run(fn,text):
    lexer = Lexer(fn,text)
    tokens,error = lexer.make_tokens()
    if error : return tokens , error

    ### AST

    parser = Parser(tokens)
    ast = parser.parse()
    return ast , None