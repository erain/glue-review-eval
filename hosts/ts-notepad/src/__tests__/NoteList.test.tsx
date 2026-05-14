import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import NoteList from '../components/NoteList';

const notes = [
  { id: 'a', body: '# Alpha', title: 'Alpha', createdAt: 1, updatedAt: 2 },
  { id: 'b', body: 'Beta line', title: 'Beta line', createdAt: 3, updatedAt: 4 },
];

describe('NoteList', () => {
  it('renders an empty-state message when there are no notes', () => {
    render(
      <NoteList
        notes={[]}
        selectedId={null}
        onSelect={() => {}}
        onCreate={() => {}}
        onDelete={() => {}}
      />,
    );
    expect(screen.getByText(/no notes yet/i)).toBeInTheDocument();
  });

  it('renders titles and marks the selected one', () => {
    render(
      <NoteList
        notes={notes}
        selectedId="b"
        onSelect={() => {}}
        onCreate={() => {}}
        onDelete={() => {}}
      />,
    );
    expect(screen.getByText('Alpha')).toBeInTheDocument();
    const selected = screen.getByRole('option', { name: /beta line/i });
    expect(selected).toHaveAttribute('aria-selected', 'true');
  });

  it('calls onSelect when a row is clicked', () => {
    const onSelect = vi.fn();
    render(
      <NoteList
        notes={notes}
        selectedId="a"
        onSelect={onSelect}
        onCreate={() => {}}
        onDelete={() => {}}
      />,
    );
    fireEvent.click(screen.getByRole('option', { name: /beta line/i }));
    expect(onSelect).toHaveBeenCalledWith('b');
  });

  it('calls onCreate when New is clicked', () => {
    const onCreate = vi.fn();
    render(
      <NoteList
        notes={notes}
        selectedId="a"
        onSelect={() => {}}
        onCreate={onCreate}
        onDelete={() => {}}
      />,
    );
    fireEvent.click(screen.getByRole('button', { name: /new note/i }));
    expect(onCreate).toHaveBeenCalledTimes(1);
  });

  it('disables Delete when nothing is selected', () => {
    const onDelete = vi.fn();
    render(
      <NoteList
        notes={notes}
        selectedId={null}
        onSelect={() => {}}
        onCreate={() => {}}
        onDelete={onDelete}
      />,
    );
    const del = screen.getByRole('button', { name: /delete selected note/i });
    expect(del).toBeDisabled();
    fireEvent.click(del);
    expect(onDelete).not.toHaveBeenCalled();
  });

  it('passes the selected id to onDelete', () => {
    const onDelete = vi.fn();
    render(
      <NoteList
        notes={notes}
        selectedId="a"
        onSelect={() => {}}
        onCreate={() => {}}
        onDelete={onDelete}
      />,
    );
    fireEvent.click(screen.getByRole('button', { name: /delete selected note/i }));
    expect(onDelete).toHaveBeenCalledWith('a');
  });
});
