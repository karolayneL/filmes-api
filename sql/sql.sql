CREATE TABLE movies (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    release_year INTEGER NOT NULL CHECK (release_year >= 1888 AND release_year <= EXTRACT(YEAR FROM CURRENT_DATE)),
    duration INTEGER NOT NULL CHECK (duration > 0),
    genre VARCHAR(100) NOT NULL,
    director VARCHAR(100) NOT NULL,
    rating DECIMAL(3,1) NOT NULL CHECK (rating >= 0 AND rating <= 10),
    user_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Habilitar RLS (Row Level Security)
ALTER TABLE movies ENABLE ROW LEVEL SECURITY;

-- Política: usuários autenticados podem ver todos os filmes
CREATE POLICY "Users can view all movies" ON movies
    FOR SELECT USING (auth.role() = 'authenticated');

-- Política: usuários só podem inserir seus próprios filmes
CREATE POLICY "Users can insert their own movies" ON movies
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Política: usuários só podem atualizar seus próprios filmes
CREATE POLICY "Users can update their own movies" ON movies
    FOR UPDATE USING (auth.uid() = user_id);

-- Política: usuários só podem deletar seus próprios filmes
CREATE POLICY "Users can delete their own movies" ON movies
    FOR DELETE USING (auth.uid() = user_id);